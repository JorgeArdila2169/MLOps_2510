from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pathlib
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import mlflow.pyfunc
import mlflow
import os

# Cargar variables de entorno desde .env
env_path = pathlib.Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL")
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("MINIO_ROOT_USER")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("MINIO_ROOT_PASSWORD")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_SERVER_URI")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

app = FastAPI()

# Cargar modelo desde MLflow
MODEL_NAME = "best_model"
MODEL_STAGE = "Production"
client = mlflow.tracking.MlflowClient()

try:
    model_version = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])[0].version
    model_uri = f"models:/{MODEL_NAME}/{model_version}"
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"Modelo '{MODEL_NAME}' v{model_version} cargado correctamente.")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    model = None

# Columnas usadas en el entrenamiento
NUMERIC_FEATURES = [
    "Elevation", "Hillshade_9am", "Hillshade_Noon", "Horizontal_Distance_To_Fire_Points",
    "Horizontal_Distance_To_Hydrology", "Horizontal_Distance_To_Roadways", "Slope",
    "Vertical_Distance_To_Hydrology"
]
CATEGORICAL_FEATURES = ["Soil_Type", "Wilderness_Area"]

# Modelo de entrada
class PredictionInput(BaseModel):
    Elevation: float
    Hillshade_9am: float
    Hillshade_Noon: float
    Horizontal_Distance_To_Fire_Points: float
    Horizontal_Distance_To_Hydrology: float
    Horizontal_Distance_To_Roadways: float
    Slope: float
    Vertical_Distance_To_Hydrology: float
    Soil_Type: str
    Wilderness_Area: str

@app.get("/")
def home():
    return {"message": "API para predicción de Cover_Type (forest cover)"}

@app.post("/predict/")
def predict(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible actualmente")

    try:
        df = pd.DataFrame([input_data.dict()])

        # Escalar numéricas
        scaler = StandardScaler()
        df[NUMERIC_FEATURES] = scaler.fit_transform(df[NUMERIC_FEATURES])

        # Codificar categóricas
        for col in CATEGORICAL_FEATURES:
            encoder = LabelEncoder()
            df[col] = encoder.fit_transform(df[col])

        prediction = model.predict(df)[0]

        return {
            "input": input_data.dict(),
            "prediction": int(prediction)
        }

    except Exception as e:
        print(f"Error en la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al hacer la predicción: {e}")
