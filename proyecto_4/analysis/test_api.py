import requests
import json

# Endpoint base
BASE_URL = "http://10.43.101.108:80/data"

# Parámetros de consulta (ajústalos según tu grupo y día)
params = {
    "group_number": 5,
    "day": "Wednesday"
}

try:
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    print("✅ Respuesta recibida.\n")

    # Si es una lista directa
    if isinstance(data, list):
        print("📦 Lista de datos (mostrando primeros 5 registros):\n")
        for i, item in enumerate(data[:5]):
            print(f"Registro {i+1}:\n{json.dumps(item, indent=2)}\n")

    # Si es un diccionario, mostrar claves y primeros registros si aplica
    elif isinstance(data, dict):
        print(f"🔍 Diccionario recibido con llaves: {list(data.keys())}\n")
        # Buscamos el primer campo que sea una lista
        for key, value in data.items():
            if isinstance(value, list):
                print(f"📦 Campo '{key}' contiene una lista. Mostrando primeros 5 registros:\n")
                for i, item in enumerate(value[:5]):
                    print(f"Registro {i+1}:\n{json.dumps(item, indent=2)}\n")
                break
        else:
            print("⚠️ No se encontró ninguna lista en la respuesta.")
    else:
        print("⚠️ Tipo de dato inesperado:", type(data))

except requests.exceptions.RequestException as e:
    print(f"❌ Error en la solicitud: {e}")
except json.decoder.JSONDecodeError:
    print("⚠️ La respuesta no es JSON válida:")
    print(response.text[:500])
