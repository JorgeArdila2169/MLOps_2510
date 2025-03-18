from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import mlflow.pyfunc
import os

# Configurar credenciales de MinIO para MLflow
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://10.43.101.165:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "supersecret"

app = FastAPI()

# Configurar conexión a MLflow
MLFLOW_TRACKING_URI = "http://10.43.101.165:5000"  
MODEL_NAME = "best_model"
MODEL_STAGE = "Production"

# Configurar cliente de MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = mlflow.tracking.MlflowClient()

# Obtener la última versión del modelo en Producción
try:
    model_version = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])[0].version
    print(f"Cargando modelo '{MODEL_NAME}' versión {model_version} desde MLflow...")
except IndexError:
    raise RuntimeError(f"No se encontró un modelo en stage '{MODEL_STAGE}' para '{MODEL_NAME}'.")

# Cargar el modelo desde MLflow
model_uri = f"models:/{MODEL_NAME}/{model_version}"
model = mlflow.pyfunc.load_model(model_uri)
print(f"Modelo {MODEL_NAME} v{model_version} cargado correctamente desde MLflow.")

# Mapeo de etiquetas
label_mapping = {0: "FEMALE", 1: "MALE"}

# Modelo de entrada para la API
class PredictionInput(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

@app.get("/")
def home():
    """Bienvenida a la API"""
    return {"message": "Bienvenido a la API de predicción de pingüinos"}

@app.post("/predict/")
def predict(input_data: PredictionInput):
    """Realiza una predicción con el modelo de MLflow"""
    try:
        # Convertir entrada en array NumPy
        features_array = np.array([[input_data.culmen_length_mm,
                                    input_data.culmen_depth_mm,
                                    input_data.flipper_length_mm,
                                    input_data.body_mass_g]], dtype=np.float64)
        
        # Hacer predicción con el modelo de MLflow
        prediction = model.predict(features_array)[0]
        prediction_label = label_mapping.get(int(prediction), "UNKNOWN")

        if np.isnan(prediction) or np.isinf(prediction):
            raise ValueError("La predicción generó un valor inválido (NaN o inf).")

        return {
            "input": input_data.dict(),
            "prediction": prediction_label
        }

    except Exception as e:
        print(f"Error en la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al hacer la predicción: {e}")
