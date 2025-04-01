from fastapi import FastAPI, HTTPException
import mlflow.pyfunc
import pandas as pd
import requests

app = FastAPI()

# Cargar el modelo desde MLflow
model_uri = "models:/forest_cover_prediction/latest"
model = mlflow.pyfunc.load_model(model_uri)

# API de datos (ajustada con la URL correcta)
DATA_API_URL = "http://10.43.101.201:80/data"

@app.get("/")
def home():
    return {"message": "API de Inferencia activa"}

@app.get("/predict-from-data")
def predict_from_data(group_number: int):
    # 1️⃣ Solicitar datos desde la API externa con el parámetro correcto
    response = requests.get(f"{DATA_API_URL}?group_number={group_number}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error al obtener datos")

    data_response = response.json()
    batch_data = data_response.get("data", [])

    if not batch_data:
        raise HTTPException(status_code=400, detail="No hay datos disponibles")

    # 2️⃣ Convertir datos a DataFrame
    df = pd.DataFrame(batch_data)

    # 3️⃣ Realizar la predicción
    prediction = model.predict(df)

    # 4️⃣ Devolver la predicción
    return {
        "group_number": group_number,
        "batch_number": data_response.get("batch_number"),
        "predictions": prediction.tolist()
    }

