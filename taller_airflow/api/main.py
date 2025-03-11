from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import os

app = FastAPI()

# Ruta del modelo
MODEL_PATH = "/models/xgboost_model.pkl"

# Cargar el modelo al iniciar la API
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"❌ No se encontró el modelo en {MODEL_PATH}")

model = joblib.load(MODEL_PATH)
print("✅ Modelo cargado correctamente")

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
    return {"message": "Bienvenido a la API de predicción de pingüinos 🐧"}

@app.post("/predict/")
def predict(input_data: PredictionInput):
    """Realiza una predicción con el modelo de XGBoost"""
    try:
        # Convertir entrada en array NumPy
        features_array = np.array([[input_data.culmen_length_mm,
                                    input_data.culmen_depth_mm,
                                    input_data.flipper_length_mm,
                                    input_data.body_mass_g]], dtype=np.float64)
        
        # Predicción
        prediction = model.predict(features_array)[0]
        prediction_label = label_mapping.get(int(prediction), "UNKNOWN")

        if np.isnan(prediction) or np.isinf(prediction):
            raise ValueError("La predicción generó un valor inválido (NaN o inf).")

        return {
            "input": input_data.dict(),
            "prediction": prediction_label
        }

    except Exception as e:
        print(f"⚠️ Error en la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al hacer la predicción: {e}")