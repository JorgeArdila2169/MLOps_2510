import requests
import json
import time

URL = "http://10.43.101.108:80/data"
GRUPO = 5
DIA = "Wednesday"
TIMEOUT = 60  # mayor tolerancia

params = {
    "group_number": GRUPO,
    "day": DIA
}

try:
    print("⏳ Enviando petición...")
    start = time.time()
    response = requests.get(URL, params=params, timeout=TIMEOUT)
    elapsed = time.time() - start
    response.raise_for_status()

    json_data = response.json()
    batch = json_data.get("batch_number", "desconocido")
    data = json_data.get("data", [])

    print(f"✅ Batch recibido: {batch}")
    print(f"📦 Registros: {len(data)}")
    print(f"⏱️ Tiempo de respuesta: {elapsed:.2f}s")

    # Guardar raw
    with open(f"batch_{batch}_raw.json", "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"📁 Guardado: batch_{batch}_raw.json")

except requests.exceptions.Timeout:
    print("⛔ Timeout alcanzado, puede que el batch sea pesado o esté diseñado así.")
except Exception as e:
    print(f"❌ Error: {e}")