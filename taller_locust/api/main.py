from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import os

app = FastAPI()

# Ruta del modelo 
MODEL_PATH = "random_forest_model.pkl"

# Cargamos el modelo al iniciar la aplicación
try:
    model = joblib.load(MODEL_PATH)
    print(f"Modelo cargado correctamente desde {MODEL_PATH}")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    raise RuntimeError(f"No se pudo cargar el modelo: {e}")

# Mapeo de la predicción numérica a la clase
label_mapping = {0: "FEMALE", 1: "MALE"}

# Esquema de datos para la predicción
class PredictionInput(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

@app.post("/predict/")
def predict(input_data: PredictionInput):
    """Hace una predicción con el modelo cargado."""
    try:
        # Convertir la entrada en un array de NumPy
        features_array = np.array([[
            input_data.culmen_length_mm,
            input_data.culmen_depth_mm,
            input_data.flipper_length_mm,
            input_data.body_mass_g
        ]], dtype=np.float64)

        prediction = model.predict(features_array)[0]
        prediction_label = label_mapping.get(int(prediction), "UNKNOWN")

        # Verificar si la predicción es válida
        if np.isnan(prediction) or np.isinf(prediction):
            raise ValueError("La predicción generó un valor inválido (NaN o inf).")

        return {
            "input": {
                "culmen_length_mm": input_data.culmen_length_mm,
                "culmen_depth_mm": input_data.culmen_depth_mm,
                "flipper_length_mm": input_data.flipper_length_mm,
                "body_mass_g": input_data.body_mass_g,
            },
            "prediction": prediction_label
        }

    except Exception as e:
        print(f"Error en la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al hacer la predicción: {e}")
