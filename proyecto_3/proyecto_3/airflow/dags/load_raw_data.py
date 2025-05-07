from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import sqlalchemy
import os
import requests

def load_csv_to_mysql():
    # Conexión
    user = os.environ['DATA_MYSQL_USER']
    password = os.environ['DATA_MYSQL_PASSWORD']
    host = os.environ['DATA_MYSQL_HOST']
    db = os.environ['DATA_MYSQL_DATABASE']
    port = os.environ.get('DATA_MYSQL_PORT', 3306)

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    engine = sqlalchemy.create_engine(connection_string)

    # Ruta dentro del contenedor de Airflow
    data_root = '/opt/airflow/data/Diabetes'
    os.makedirs(data_root, exist_ok=True)
    data_filepath = os.path.join(data_root, 'Diabetes.csv')

    # Si no existe el archivo, descargarlo
    if not os.path.isfile(data_filepath):
        url = 'https://docs.google.com/uc?export=download&id=1k5-1caezQ3zWJbKaiMULTGq-3sz6uThC'
        print("Downloading dataset from", url)
        r = requests.get(url, allow_redirects=True, stream=True)
        with open(data_filepath, 'wb') as f:
            f.write(r.content)
        print("Download completed.")

    # Leer CSV
    df = pd.read_csv(data_filepath)

    # Renombrar columnas
    df.columns = df.columns.str.replace('-', '_')

    # Insertar en MySQL
    df.to_sql('raw_data', con=engine, if_exists='append', index=False)

default_args = {
    'start_date': datetime(2025, 5, 5),
    'retries': 1
}

with DAG('load_csv_to_raw_data',
         schedule_interval=None,
         default_args=default_args,
         catchup=False) as dag:

    load_task = PythonOperator(
        task_id='download_and_load_csv_to_mysql',
        python_callable=load_csv_to_mysql
    )
