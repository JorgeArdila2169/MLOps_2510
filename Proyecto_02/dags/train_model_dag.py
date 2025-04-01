from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import json
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Configuración del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 18),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'train_model',
    default_args=default_args,
    description='DAG para preprocesar datos y entrenar un modelo',
    schedule_interval=timedelta(hours=1),
    catchup=False,
)

def preprocess_data():
    with open('/opt/airflow/data/dataset.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    df = df.dropna()
    df.to_csv('/opt/airflow/data/clean_data.csv', index=False)
    print("Datos preprocesados y guardados correctamente.")

def train_model():
    df = pd.read_csv('/opt/airflow/data/clean_data.csv')
    X = df.drop(columns=['target'])  # Ajusta según la estructura de tus datos
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("forest_cover_prediction")
    
    with mlflow.start_run():
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(model, "model")
    
    print(f"Modelo entrenado con accuracy: {accuracy}")

preprocess_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

preprocess_task >> train_task

