import requests
import random
import time

API_URL = "http://api-service:8000/predict"

while True:
    data = {
        "data": [[random.uniform(4.0, 8.0) for _ in range(4)]]
    }
    try:
        requests.post(API_URL, json=data)
    except Exception as e:
        print("Error:", e)
    time.sleep(1)