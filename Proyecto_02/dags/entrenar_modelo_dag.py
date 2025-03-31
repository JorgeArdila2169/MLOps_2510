# dags/entrenar_modelo_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os
import glob
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Rutas
RAW_DIR = "/opt/airflow/data/raw"
PROCESSED_DIR = "/opt/airflow/data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Función para entrenar modelo con MLflow
def entrenar_modelo():
    all_files = glob.glob(os.path.join(RAW_DIR, "batch_*.csv"))
    if len(all_files) < 10:
        print("No hay suficientes batches para entrenar el modelo.")
        return

    df_list = [pd.read_csv(f) for f in all_files]
    df = pd.concat(df_list, ignore_index=True)

    # Limpieza básica de datos (puedes personalizar esto)
    df.dropna(inplace=True)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("Proyecto2")

    with mlflow.start_run():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(clf, "model")

        print(f"Modelo entrenado con accuracy: {acc}")

# DAG para entrenamiento
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'entrenar_modelo',
    default_args=default_args,
    description='Entrena un modelo con los datos recolectados y lo registra en MLflow',
    schedule_interval=None,
    catchup=False,
)

tarea_entrenar = PythonOperator(
    task_id='entrenar_modelo_mlflow',
    python_callable=entrenar_modelo,
    dag=dag
)

tarea_entrenar
