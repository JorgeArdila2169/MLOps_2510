from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import os
import pandas as pd

# Configuración del DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

# Ruta donde se guardarán los datos
INGESTION_PATH = "/airflow/ingestion_data"
API_URL = "http://10.43.101.201:80"
GRUPO_ID = 5  # <-- CAMBIA ESTO por el número de tu grupo

# Función para recolectar y guardar los datos
def fetch_and_store_data():
    response = requests.get(f"{API_URL}/data?group_number={GRUPO_ID}")
    response.raise_for_status()
    payload = response.json()

    batch_data = payload["data"]

    # Define columnas según el orden del CSV original (ajusta si las cambian)
    column_names = [
        "Elevation",
        "Aspect",
        "Slope",
        "Horizontal_Distance_To_Hydrology",
        "Vertical_Distance_To_Hydrology",
        "Horizontal_Distance_To_Roadways",
        "Hillshade_9am",
        "Hillshade_Noon",
        "Hillshade_3pm",
        "Horizontal_Distance_To_Fire_Points",
        "Wilderness_Area",
        "Soil_Type",
        "Cover_Type"
    ]

    df = pd.DataFrame(batch_data, columns=column_names)

    os.makedirs(INGESTION_PATH, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(INGESTION_PATH, f"batch_{timestamp}.csv")
    df.to_csv(file_path, index=False)
    print(f"Datos guardados en {file_path}")

# Definir el DAG
with DAG(
    dag_id="data_ingestion_from_external_api",
    default_args=default_args,
    description="Ingesta de datos cada 5 minutos desde una API externa",
    schedule_interval="*/5 * * * *",  # cada 5 minutos
    start_date=datetime(2025, 4, 4),
    catchup=False,
    tags=["ingestion", "mlflow"]
) as dag:

    ingest_task = PythonOperator(
        task_id="fetch_and_store_data",
        python_callable=fetch_and_store_data
    )

    ingest_task
