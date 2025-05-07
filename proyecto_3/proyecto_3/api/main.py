from pydantic import BaseModel
from typing import List
import mlflow
from mlflow.tracking import MlflowClient
import os
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from fastapi import FastAPI
import pandas as pd

# Configuración
MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://mlflow:5000')
EXPERIMENT_NAME = 'diabetes_prediction_rf'

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient()

# Cargar el mejor modelo
experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string="tags.best_model = 'true'"
)

if not runs:
    raise Exception("No best_model tag found in any run.")

best_run = runs[0]
model_uri = f"{best_run.info.artifact_uri}/model"
model = mlflow.pyfunc.load_model(model_uri)

print(f"Loaded model from {model_uri}")

app = FastAPI()

# Métricas de Prometheus
predict_counter = Counter("predictions_total", "Total number of predictions")
class_counter = Counter("predicted_classes", "Count per predicted class", ["class"])
REQUEST_LATENCY = Histogram("predict_latency_seconds", "Tiempo de latencia de predicción")

class FeatureInput(BaseModel):
    num_lab_procedures: float
    num_medications: float
    time_in_hospital: float
    number_inpatient: float
    A1Cresult: str  

class InputData(BaseModel):
    data: List[FeatureInput] 

@app.post("/predict")
def predict(input_data: InputData):
    predict_counter.inc()

    # Convertimos a DataFrame
    input_df = pd.DataFrame([feature.dict() for feature in input_data.data])

    # Mapear A1Cresult
    a1c_map = {'None': 0, 'Norm': 0, '>7': 1, '>8': 1}
    input_df['A1Cresult'] = input_df['A1Cresult'].map(a1c_map).fillna(0)
    
    # Convertir las entradas numéricas a int
    input_df['num_lab_procedures'] = input_df['num_lab_procedures'].astype(int)
    input_df['num_medications'] = input_df['num_medications'].astype(int)
    input_df['time_in_hospital'] = input_df['time_in_hospital'].astype(int)
    input_df['number_inpatient'] = input_df['number_inpatient'].astype(int)

    with REQUEST_LATENCY.time():
        preds = model.predict(input_df)

    for pred in preds:
        class_counter.labels(str(pred)).inc()

    return {
        "predictions": preds.tolist() if hasattr(preds, 'tolist') else preds,
        "model_info": {
            "run_id": best_run.info.run_id,
            "artifact_uri": best_run.info.artifact_uri,
            "tag": "best_model"
        }
    }

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
