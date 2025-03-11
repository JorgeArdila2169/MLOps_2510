from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
import pandas as pd
from datetime import datetime

# Función para preprocesar y guardar en MySQL
def preprocess_penguins():
    mysql_hook = MySqlHook(mysql_conn_id="mysql_penguins")
    
    # Cargar datos desde MySQL
    sql_query = "SELECT * FROM penguins"
    df = mysql_hook.get_pandas_df(sql_query)

    # Eliminar filas donde el sexo es 0
    df = df[df["sex"] != 0]

    # Eliminar las columnas de especie e isla
    df = df.drop(columns=["species", "island"])

    # Filtrar solo filas donde 'sex' es válido
    df = df[df["sex"].isin(["MALE", "FEMALE"])]

    # Mapear el sexo: MALE -> 1, FEMALE -> 0
    df["sex"] = df["sex"].map({"MALE": 1, "FEMALE": 0})

    # Dividir los datos en entrenamiento (80%), validación (10%) y prueba (10%)
    train_df = df.sample(frac=0.8, random_state=200)
    rest_df = df.drop(train_df.index)
    val_df = rest_df.sample(frac=0.5, random_state=200)
    test_df = rest_df.drop(val_df.index)

    # Guardar los datos en MySQL
    conn = mysql_hook.get_sqlalchemy_engine()

    # Borrar tablas previas si existen
    with conn.begin() as connection:
        connection.execute("DROP TABLE IF EXISTS train_penguins")
        connection.execute("DROP TABLE IF EXISTS val_penguins")
        connection.execute("DROP TABLE IF EXISTS test_penguins")

    # Guardar cada conjunto en MySQL
    train_df.to_sql("train_penguins", conn, if_exists="replace", index=False)
    val_df.to_sql("val_penguins", conn, if_exists="replace", index=False)
    test_df.to_sql("test_penguins", conn, if_exists="replace", index=False)

# Configuración del DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 3, 11),
    "retries": 1,
}

dag = DAG(
    "preprocess_penguins",
    default_args=default_args,
    description="Preprocesa los datos de pingüinos desde MySQL y guarda en MySQL",
    schedule_interval=None,
    catchup=False,
)

# Definir la tarea
preprocess_task = PythonOperator(
    task_id="preprocess_data",
    python_callable=preprocess_penguins,
    dag=dag,
)

preprocess_task