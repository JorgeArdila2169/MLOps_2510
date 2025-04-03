from locust import HttpUser, task, between
from pydantic import BaseModel, ValidationError

class PredictionInput(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

class InferenceUser(HttpUser):
    # Tiempo de espera entre tareas para simular comportamiento real
    wait_time = between(1, 2)
    
    host = "http://api:8000"
    
    @task(3)
    def valid_prediction(self):
        try:
            # Construir el payload
            payload = PredictionInput(
                culmen_length_mm=42.2,
                culmen_depth_mm=18.5,
                flipper_length_mm=180.0,
                body_mass_g=3550.0
            )
        except ValidationError as e:
            self.environment.runner.quit()
            return
        
        with self.client.post("/predict/", json=payload.dict(), catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Fallo en predicción válida, status code: {response.status_code}")