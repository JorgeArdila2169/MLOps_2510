from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json

# Configuración del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 18),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fetch_data_from_api',
    default_args=default_args,
    description='DAG para recolectar datos de la API externa cada 5 minutos',
    schedule_interval=timedelta(minutes=5),
    catchup=False,
)

def fetch_data():
    api_url = "http://10.43.101.201:80/data"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        with open('/opt/airflow/data/dataset.json', 'w') as f:
            json.dump(data, f)
        print("Datos guardados correctamente")
    else:
        print(f"Error en la solicitud: {response.status_code}")

fetch_data_task = PythonOperator(
    task_id='fetch_data_task',
    python_callable=fetch_data,
    dag=dag,
)

fetch_data_task

