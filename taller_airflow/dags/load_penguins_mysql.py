import pandas as pd
import numpy as np
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime

# Ruta del archivo CSV
CSV_PATH = "/opt/airflow/data/penguins_size.csv"

# Función para cargar datos en MySQL
def load_csv_to_mysql():
    mysql_hook = MySqlHook(mysql_conn_id="mysql_penguins") 
    conn = mysql_hook.get_conn()
    cursor = conn.cursor()

    # Leer CSV en un DataFrame
    df = pd.read_csv(CSV_PATH)
    df = df.fillna(0)

    # Crear tabla si no existe
    create_table_query = """
    CREATE TABLE IF NOT EXISTS penguins (
        species VARCHAR(50),
        island VARCHAR(50),
        bill_length_mm FLOAT,
        bill_depth_mm FLOAT,
        flipper_length_mm FLOAT,
        body_mass_g FLOAT,
        sex VARCHAR(10)
    );
    """
    cursor.execute(create_table_query)

    # Insertar los datos en la tabla
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO penguins (species, island, bill_length_mm, bill_depth_mm, flipper_length_mm, body_mass_g, sex) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            tuple(row)
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("Datos insertados en MySQL correctamente")

# Definir el DAG en Airflow
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 10),
    'retries': 1
}

with DAG(
    dag_id="load_penguins_mysql",
    default_args=default_args,
    schedule_interval=None,  # Se ejecuta manualmente
    catchup=False,
    description="Carga los datos de penguins.csv en la base de datos MySQL"
) as dag:

    load_task = PythonOperator(
        task_id="load_csv_to_mysql",
        python_callable=load_csv_to_mysql
    )

    load_task