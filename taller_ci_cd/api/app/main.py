from fastapi import FastAPI
from pydantic import BaseModel
import pickle
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response

app = FastAPI()

class InputData(BaseModel):
    data: list  

# Métrica personalizada
prediction_counter = Counter("predictions_total", "Número de predicciones realizadas")

# Cargar modelo
with open("app/model.pkl", "rb") as f:
    model = pickle.load(f)

@app.post("/predict")
def predict(input: InputData):
    prediction_counter.inc()
    prediction = model.predict(input.data).tolist()
    return {"prediction": prediction}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")