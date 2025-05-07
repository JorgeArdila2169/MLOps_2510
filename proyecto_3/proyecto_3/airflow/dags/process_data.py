from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import sqlalchemy
import os

def process_subset(table_name, cleaned_table_name):
    user = os.environ['DATA_MYSQL_USER']
    password = os.environ['DATA_MYSQL_PASSWORD']
    host = os.environ['DATA_MYSQL_HOST']
    db = os.environ['DATA_MYSQL_DATABASE']
    port = os.environ.get('DATA_MYSQL_PORT', 3306)

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    engine = sqlalchemy.create_engine(connection_string)

    # Leer el subconjunto
    df = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)

    # Filtrar solo las variables seleccionadas + target
    variables = [
        'num_lab_procedures',
        'num_medications',
        'time_in_hospital',
        'number_inpatient',
        'A1Cresult',
        'readmitted'
    ]
    df = df[variables]

    # Mapear A1Cresult
    a1c_map = {'None':0, 'Norm':0, '>7':1, '>8':1}
    df['A1Cresult'] = df['A1Cresult'].map(a1c_map).fillna(0)

    # Mapear readmitted
    readmitted_map = {'NO':0, '>30':0, '<30':1}
    df['readmitted'] = df['readmitted'].map(readmitted_map).fillna(0)

    # Guardar en nueva tabla
    df.to_sql(cleaned_table_name, con=engine, if_exists='replace', index=False)
    print(f"{cleaned_table_name} created with {len(df)} records.")

default_args = {'start_date': datetime(2025, 5, 5)}

with DAG('process_data_subsets',
         schedule_interval=None,
         default_args=default_args,
         catchup=False) as dag:

    process_train = PythonOperator(
        task_id='process_train_data',
        python_callable=process_subset,
        op_args=['train_data', 'train_data_cleaned']
    )

    process_val = PythonOperator(
        task_id='process_validation_data',
        python_callable=process_subset,
        op_args=['validation_data', 'validation_data_cleaned']
    )

    process_test = PythonOperator(
        task_id='process_test_data',
        python_callable=process_subset,
        op_args=['test_data', 'test_data_cleaned']
    )

    process_train >> process_val >> process_test
