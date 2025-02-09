from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="API de Inferencia de Modelos")

# Cargar los modelos
model_paths = {
    "random_forest": "models/random_forest_model.pkl",
    "logistic_regression": "models/logistic_regression_model.pkl"
}

models = {name: joblib.load(path) for name, path in model_paths.items()}

# Variable global para almacenar el modelo seleccionado
selected_model = "random_forest" 

label_mapping = {0: "Female", 1: "Male"}

# Definir esquema de entrada para la API
class PredictionInput(BaseModel):
    features: list[float]  

class ModelSelectionInput(BaseModel):
    model_name: str  

# Ruta de prueba
@app.get("/")
def home():
    return {"message": "API de Inferencia Activa"}

# Endpoint para seleccionar el modelo manualmente
@app.post("/set_model/")
def set_model(input_data: ModelSelectionInput):
    global selected_model 

    model_name = input_data.model_name.lower()
    if model_name not in models:
        raise HTTPException(status_code=400, detail="Modelo no válido. Usa 'random_forest' o 'logistic_regression'.")
    
    selected_model = model_name
    return {"message": f"Modelo seleccionado: {selected_model}"}

# Endpoint para hacer predicciones usando el modelo seleccionado
@app.post("/predict/")
def predict(input_data: PredictionInput):
    model = models[selected_model]  
    
    # Convertir los datos de entrada en un array de NumPy
    features_array = np.array([input_data.features])
    
    # Predicción
    prediction = model.predict(features_array)[0]
    prediction_label = label_mapping.get(int(prediction), "Unknown")

    return {
        "model_used": selected_model,
        "input_features": input_data.features,
        "predicted_label": prediction_label
    }

