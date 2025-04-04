from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime

# Función para borrar todas las tablas de la base de datos
def clear_mysql_tables():
    mysql_hook = MySqlHook(mysql_conn_id="mysql_penguins") 
    conn = mysql_hook.get_conn()
    cursor = conn.cursor()

    # Obtener todas las tablas en la BD
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    # Borrar datos de cada tabla
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DELETE FROM {table_name};")
        print(f"✔️ Se eliminaron los datos de la tabla: {table_name}")

    conn.commit()
    cursor.close()
    conn.close()

# Definir el DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 10),
    'retries': 1
}

with DAG(
    dag_id="clear_mysql_db",
    default_args=default_args,
    schedule_interval=None,  # Solo se ejecuta manualmente
    catchup=False,
    description="Borra todas las tablas de la BD MySQL penguins_db"
) as dag:

    clear_db_task = PythonOperator(
        task_id="clear_mysql_tables",
        python_callable=clear_mysql_tables
    )

    clear_db_task