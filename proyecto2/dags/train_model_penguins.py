from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
import pandas as pd
import xgboost as xgb
import joblib
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime
import os

def train_xgboost():
    # Conectar a MySQL
    mysql_hook = MySqlHook(mysql_conn_id='mysql_penguins')
    
    # Leer datos de entrenamiento desde MySQL
    train_query = "SELECT * FROM train_penguins;"
    train_df = mysql_hook.get_pandas_df(train_query)
    
    # Separar features y etiquetas
    y_train = train_df.pop("sex")
    X_train = train_df
    
    # Leer datos de test desde MySQL
    test_query = "SELECT * FROM test_penguins;"
    test_df = mysql_hook.get_pandas_df(test_query)
    
    # Separar features y etiquetas
    y_test = test_df.pop("sex")
    X_test = test_df
    
    # Entrenar el modelo XGBoost
    xg_model = xgb.XGBClassifier(eval_metric='logloss')
    xg_model.fit(X_train, y_train)
    
    # Hacer predicciones y evaluar el modelo
    y_pred = xg_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Female (0)", "Male (1)"])
    
    print(f"Accuracy: {accuracy:.2f}")
    print("\n🔹 Classification Report:\n", report)
    
    # Guardar el modelo
    model_path = "/opt/airflow/models/xgboost_model.pkl"
    joblib.dump(xg_model, model_path)
    print(f"Modelo guardado en {model_path}")

# Definir DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 11),
    'retries': 1,
}

dag = DAG(
    'train_xgboost',
    default_args=default_args,
    description='Entrena un modelo XGBoost con datos de MySQL y guarda el modelo',
    schedule_interval=None,
)

train_task = PythonOperator(
    task_id='train_xgboost_model',
    python_callable=train_xgboost,
    dag=dag,
)

train_task