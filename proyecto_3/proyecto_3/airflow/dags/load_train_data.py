from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import sqlalchemy
import os

def load_train_batch():
    user = os.environ['DATA_MYSQL_USER']
    password = os.environ['DATA_MYSQL_PASSWORD']
    host = os.environ['DATA_MYSQL_HOST']
    db = os.environ['DATA_MYSQL_DATABASE']
    port = os.environ.get('DATA_MYSQL_PORT', 3306)

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    engine = sqlalchemy.create_engine(connection_string)

    # Leer todo raw_data
    df_raw = pd.read_sql('SELECT * FROM raw_data', con=engine)

    # 70% train, 15% val, 15% test
    train_size = int(0.7 * len(df_raw))
    df_train = df_raw.iloc[:train_size]

    # Leer cuántos registros ya existen en train_data
    try:
        existing_rows = pd.read_sql('SELECT COUNT(*) as count FROM train_data', con=engine)['count'][0]
    except Exception:
        existing_rows = 0 
        
    batch_size = 15000
    next_batch = df_train.iloc[existing_rows:existing_rows + batch_size]

    if next_batch.empty:
        print("No more records to insert.")
        return

    next_batch.to_sql('train_data', con=engine, if_exists='append', index=False)
    print(f"Inserted batch: {existing_rows} - {existing_rows + len(next_batch)}")

default_args = {'start_date': datetime(2025, 5, 5)}

with DAG('load_train_data_batches',
         schedule_interval=None,
         default_args=default_args,
         catchup=False) as dag:

    load_train_task = PythonOperator(
        task_id='load_train_batch',
        python_callable=load_train_batch
    )
