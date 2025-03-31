# dags/recolectar_datos_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import os
import json
import pandas as pd

# Configuraciones
GROUP_NUMBER = 1  # Cambia esto por tu número de grupo
DATA_API_URL = f"http://10.43.101.108:80/data?group_number={GROUP_NUMBER}"
OUTPUT_DIR = "/opt/airflow/data/raw"

# Asegura que el directorio exista
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Función para recolectar datos de la API
def recolectar_batch():
    try:
        response = requests.get(DATA_API_URL)
        if response.status_code == 200:
            payload = response.json()
            data = payload["data"]
            batch_number = payload["batch_number"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(OUTPUT_DIR, f"batch_{batch_number}_{timestamp}.csv")
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            print(f"Datos guardados en {file_path}")
        else:
            print(f"Error al consultar la API: {response.status_code}")
    except Exception as e:
        print(f"Excepción al recolectar datos: {e}")

# Definición del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'recolectar_datos',
    default_args=default_args,
    description='Recolecta datos desde la API externa cada 2 minutos',
    schedule_interval=timedelta(minutes=2),
    catchup=False,
)

tarea_recolectar = PythonOperator(
    task_id='recolectar_batch',
    python_callable=recolectar_batch,
    dag=dag
)

tarea_recolectar
