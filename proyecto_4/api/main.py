from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
)
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import os

app = FastAPI()

# Configuración
MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://10.43.101.165:30500')
EXPERIMENT_NAME = 'house_price_regression'

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient()

# Modelo activo y su run_id
model = None
current_run_id = None

# Métricas Prometheus
predict_counter = Counter("predictions_total", "Total number of predictions")
prediction_errors = Counter("prediction_errors_total", "Errores durante la predicción")
prediction_batch_size = Histogram("prediction_batch_size", "Tamaño de cada lote de predicción")
request_latency = Histogram("predict_latency_seconds", "Prediction latency in seconds")
active_model_id = Gauge("active_model_run_id", "Run ID del modelo en producción", ["run_id"])

# Schemas
class FeatureInput(BaseModel):
    bed: float
    bath: float
    acre_lot: float
    zip_code: float
    house_size: float

class InputData(BaseModel):
    data: List[FeatureInput]

# Carga dinámica del modelo
def load_best_model():
    global model, current_run_id
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="tags.stage = 'best_model'",
        order_by=["start_time DESC"],
        max_results=1
    )

    if not runs:
        raise Exception("No best_model tagged run found.")

    best_run = runs[0]
    if best_run.info.run_id != current_run_id:
        print(f"New best model found: {best_run.info.run_id}")
        model_uri = f"runs:/{best_run.info.run_id}/model"
        model = mlflow.pyfunc.load_model(model_uri)
        current_run_id = best_run.info.run_id
        active_model_id.labels(run_id=current_run_id).set(1)

# Endpoint de predicción
@app.post("/predict")
def predict(input_data: InputData):
    predict_counter.inc()

    df = pd.DataFrame([d.dict() for d in input_data.data])
    prediction_batch_size.observe(len(df))

    try:
        load_best_model()
        with request_latency.time():
            predictions = model.predict(df)
    except Exception as e:
        prediction_errors.inc()
        raise e

    return {
        "predictions": predictions.tolist(),
        "model_info": {
            "run_id": current_run_id,
            "experiment": EXPERIMENT_NAME,
            "tag": "best_model"
        }
    }

# Endpoint de métricas para Prometheus
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

