from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import sqlalchemy
import os

def load_val_test():
    user = os.environ['DATA_MYSQL_USER']
    password = os.environ['DATA_MYSQL_PASSWORD']
    host = os.environ['DATA_MYSQL_HOST']
    db = os.environ['DATA_MYSQL_DATABASE']
    port = os.environ.get('DATA_MYSQL_PORT', 3306)

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    engine = sqlalchemy.create_engine(connection_string)

    df_raw = pd.read_sql('SELECT * FROM raw_data', con=engine)

    train_size = int(0.7 * len(df_raw))
    val_size = int(0.15 * len(df_raw))
    test_size = len(df_raw) - train_size - val_size

    df_val = df_raw.iloc[train_size:train_size + val_size]
    df_test = df_raw.iloc[train_size + val_size:]

    df_val.to_sql('validation_data', con=engine, if_exists='replace', index=False)
    df_test.to_sql('test_data', con=engine, if_exists='replace', index=False)

    print("Validation and test data inserted.")

default_args = {'start_date': datetime(2025, 5, 5)}

with DAG('load_val_test_data',
         schedule_interval=None,
         default_args=default_args,
         catchup=False) as dag:

    load_val_test_task = PythonOperator(
        task_id='load_val_test',
        python_callable=load_val_test
    )
