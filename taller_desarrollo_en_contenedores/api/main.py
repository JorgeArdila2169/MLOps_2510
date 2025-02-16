from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import numpy as np
import joblib
import os
 
app = FastAPI()
 
# Carpeta de los modelos
MODEL_DIR = "/models"
selected_model = None  
 
def get_available_models():
    """Obtiene la lista de modelos disponibles en la carpeta /models"""
    return [f for f in os.listdir(MODEL_DIR) if f.endswith(".pkl")]
 
@app.get("/models")
def list_models():
    """Lista los modelos disponibles"""
    models = get_available_models()
    return {"models": models}
 
@app.post("/select-model/")
def select_model(model_name: str = Query(..., title="Seleccionar modelo", description="Elige un modelo disponible", enum=get_available_models())):
    """
    Selecciona un modelo de la lista de modelos disponibles.
 
    - Usa una lista desplegable en Swagger UI.
    - Carga el modelo para usarlo en predicciones.
    """
    global selected_model
 
    if not model_name.endswith(".pkl"):
        model_name += ".pkl"
 
    model_path = os.path.join(MODEL_DIR, model_name)
 
    if os.path.exists(model_path):
        selected_model = joblib.load(model_path)
        return {"message": f"Modelo {model_name} cargado correctamente"}
 
    raise HTTPException(status_code=404, detail=f"Modelo no encontrado en {model_path}")
 
class PredictionInput(BaseModel):
    features: list
 
label_mapping = {0: "FEMALE", 1: "MALE"}

class PredictionInput(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

@app.post("/predict/")
def predict(input_data: PredictionInput):
    """Hace una predicción con el modelo cargado"""
    global selected_model
    if selected_model is None:
        raise HTTPException(status_code=400, detail="No hay un modelo cargado. Selecciona un modelo primero.")
 
    try:
        # Convertir la entrada en un array de NumPy
        features_array = np.array([[input_data.culmen_length_mm,
                                    input_data.culmen_depth_mm,
                                    input_data.flipper_length_mm,
                                    input_data.body_mass_g]], dtype=np.float64)
 
        prediction = selected_model.predict(features_array)[0]
        prediction_label = label_mapping.get(int(prediction), "UNKNOWN")
 
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
        print(f"⚠️ Error en la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al hacer la predicción: {e}")