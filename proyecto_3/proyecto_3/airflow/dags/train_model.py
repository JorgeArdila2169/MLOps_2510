from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import sqlalchemy
import os
import mlflow
import mlflow.sklearn
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report

def train_and_log_rf_models():
    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
    experiment_name = "diabetes_prediction_rf"
    mlflow.set_experiment(experiment_name)

    # Conexión BD
    user = os.environ['DATA_MYSQL_USER']
    password = os.environ['DATA_MYSQL_PASSWORD']
    host = os.environ['DATA_MYSQL_HOST']
    db = os.environ['DATA_MYSQL_DATABASE']
    port = os.environ.get('DATA_MYSQL_PORT', 3306)
    conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    engine = sqlalchemy.create_engine(conn_str)

    # Leer datos
    df_train = pd.read_sql('SELECT * FROM train_data_cleaned', con=engine)
    df_val = pd.read_sql('SELECT * FROM validation_data_cleaned', con=engine)
    df_test = pd.read_sql('SELECT * FROM test_data_cleaned', con=engine)

    X_train = df_train.drop('readmitted', axis=1)
    y_train = df_train['readmitted']
    X_val = df_val.drop('readmitted', axis=1)
    y_val = df_val['readmitted']
    X_test = df_test.drop('readmitted', axis=1)
    y_test = df_test['readmitted']

    # Generar hiperparámetros aleatorios
    param_grid = []
    for _ in range(10):
        params = {
            'n_estimators': random.randint(50, 200),
            'max_depth': random.choice([None, 5, 10, 20]),
            'min_samples_split': random.randint(2, 10),
            'min_samples_leaf': random.randint(1, 5)
        }
        param_grid.append(params)

    for idx, params in enumerate(param_grid, 1):
        with mlflow.start_run(run_name=f"rf_experiment_{idx}"):
            mlflow.sklearn.autolog()

            model = RandomForestClassifier(**params)
            model.fit(X_train, y_train)

            y_pred_train = model.predict(X_train)
            y_pred_val = model.predict(X_val)
            y_pred_test = model.predict(X_test)

            # Métricas resumidas
            train_report = classification_report(y_train, y_pred_train, output_dict=True, zero_division=0)
            val_report = classification_report(y_val, y_pred_val, output_dict=True, zero_division=0)
            test_report = classification_report(y_test, y_pred_test, output_dict=True, zero_division=0)

            # Log de métricas promedios ponderados
            mlflow.log_metric("train_f1", train_report["weighted avg"]["f1-score"])
            mlflow.log_metric("val_f1", val_report["weighted avg"]["f1-score"])
            mlflow.log_metric("test_f1", test_report["weighted avg"]["f1-score"])

            mlflow.log_metric("train_precision", train_report["weighted avg"]["precision"])
            mlflow.log_metric("val_precision", val_report["weighted avg"]["precision"])
            mlflow.log_metric("test_precision", test_report["weighted avg"]["precision"])

            mlflow.log_metric("train_recall", train_report["weighted avg"]["recall"])
            mlflow.log_metric("val_recall", val_report["weighted avg"]["recall"])
            mlflow.log_metric("test_recall", test_report["weighted avg"]["recall"])

            print(f"[{idx}/10] RF run logged: params={params}, test_f1={test_report['weighted avg']['f1-score']:.4f}")

default_args = {'start_date': datetime(2025, 5, 5)}

with DAG('train_random_forest',
         schedule_interval=None,
         default_args=default_args,
         catchup=False) as dag:

    train_task = PythonOperator(
        task_id='train_and_log_rf_models',
        python_callable=train_and_log_rf_models
    )
