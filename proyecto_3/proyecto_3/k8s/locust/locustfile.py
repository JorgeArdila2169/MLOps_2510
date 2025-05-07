from locust import HttpUser, task, between
import random

class DiabetesPredictionUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def predict(self):
        payload = {
            "data": [
                {
                    "num_lab_procedures": random.randint(1, 100),
                    "num_medications": random.randint(1, 50),
                    "time_in_hospital": random.randint(1, 14),
                    "number_inpatient": random.randint(0, 10),
                    "A1Cresult": random.choice(["None", "Norm", ">7", ">8"])
                }
            ]
        }
        self.client.post("/predict", json=payload)

