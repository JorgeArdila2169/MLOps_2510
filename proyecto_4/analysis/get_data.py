import requests
import pandas as pd
import time

URL = "http://10.43.101.108:80/data"
GRUPO = 5
DIA = "Wednesday"
MAX_BATCHES = 30
OUTPUT_CSV = "datos_api_explorados.csv"
TIMEOUT = 20
MAX_RETRIES = 3

registros_totales = []
errores = []

print("🔍 Iniciando exploración de batches...\n")

for i in range(MAX_BATCHES):
    print(f"➡️ Petición #{i+1}...")

    params = {"group_number": GRUPO, "day": DIA}

    for intento in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(URL, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            json_data = response.json()
            batch = json_data.get("batch_number", i)

            data = json_data.get("data", [])
            if not data:
                print(f"⚠️ Batch {batch} vacío.")
            else:
                for row in data:
                    row["batch_number"] = batch
                    registros_totales.append(row)
                print(f"✅ Batch {batch} - {len(data)} registros")

            break  # salir del retry loop

        except requests.exceptions.ReadTimeout:
            print(f"⏳ Timeout en batch {i+1} (intento {intento})")
            time.sleep(5)
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error HTTP en batch {i+1}: {e}")
            errores.append((i + 1, str(e)))
            if response.status_code == 400:
                print("🚫 La API no permite más peticiones. Deteniendo...")
                break
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            errores.append((i + 1, str(e)))
            break
    else:
        print(f"❌ Batch {i+1} falló luego de {MAX_RETRIES} intentos")
        errores.append((i + 1, "Max retries reached"))

    time.sleep(1)

# Guardar CSV
if registros_totales:
    df = pd.DataFrame(registros_totales)
    df.drop_duplicates(inplace=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n📁 Guardado en: {OUTPUT_CSV}")
    print(f"📊 Total registros únicos: {len(df)}")

if errores:
    print("\n❗Errores encontrados:")
    for b, e in errores:
        print(f"  Batch {b}: {e}")