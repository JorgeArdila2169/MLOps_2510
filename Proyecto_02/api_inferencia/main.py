# api_inferencia/main.py

from fastapi import FastAPI
from pydantic import BaseModel
import mlflow.sklearn
import pandas as pd
import os

app = FastAPI()

class InputData(BaseModel):
    features: list

# Cargar el modelo desde MLflow (última versión registrada)
MODEL_URI = "models:/Proyecto2/Production"
model = mlflow.sklearn.load_model(MODEL_URI)

@app.get("/")
def root():
    return {"message": "API de Inferencia para Proyecto MLOps"}

@app.post("/predict")
def predict(data: InputData):
    try:
        input_df = pd.DataFrame([data.features])
        prediction = model.predict(input_df)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        return {"error": str(e)}