from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import glob
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Configuración general
DATA_PATH = "/airflow/ingestion_data"
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_SERVER_URI", "http://mlflow:5000")
EXPERIMENT_NAME = "cover_type_rf_experiments"
MODEL_NAME = "best_model"

# Columnas a transformar
NUMERIC_FEATURES = [
    "Elevation", "Hillshade_9am", "Hillshade_Noon", "Horizontal_Distance_To_Fire_Points",
    "Horizontal_Distance_To_Hydrology", "Horizontal_Distance_To_Roadways", "Slope",
    "Vertical_Distance_To_Hydrology"
]
CATEGORICAL_FEATURES = ["Soil_Type", "Wilderness_Area"]
LABEL_KEY = "Cover_Type"

def preprocess(df):
    df = df.copy()

    # Escalar numéricas
    scaler = StandardScaler()
    df[NUMERIC_FEATURES] = scaler.fit_transform(df[NUMERIC_FEATURES])

    # Codificar categóricas
    for col in CATEGORICAL_FEATURES:
        encoder = LabelEncoder()
        df[col] = encoder.fit_transform(df[col])

    return df

def load_data():
    files = glob.glob(f"{DATA_PATH}/*.csv")
    if not files:
        raise FileNotFoundError("No se encontraron archivos CSV de entrada.")
    df_list = [pd.read_csv(f) for f in files]
    df = pd.concat(df_list, ignore_index=True)
    df.to_csv(f"{DATA_PATH}/full_dataset.csv", index=False)
    return df

def train_and_register_model():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    mlflow.sklearn.autolog(log_input_examples=True, log_model_signatures=True)

    df = load_data()
    df = df.dropna()
    df = preprocess(df)

    X = df.drop(columns=[LABEL_KEY])
    y = df[LABEL_KEY]

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    best_f1 = 0
    best_run_id = None

    for i in range(10):
        n_estimators = np.random.randint(50, 150)
        max_depth = np.random.choice([5, 10, 15, None])

        with mlflow.start_run(run_name=f"Experiment-{i+1}") as run:
            model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
            model.fit(X_train, y_train)

            y_pred_train = model.predict(X_train)
            y_pred_val = model.predict(X_val)
            y_pred_test = model.predict(X_test)

            train_report = classification_report(y_train, y_pred_train, output_dict=True, zero_division=0)
            val_report = classification_report(y_val, y_pred_val, output_dict=True, zero_division=0)
            test_report = classification_report(y_test, y_pred_test, output_dict=True, zero_division=0)

            mlflow.log_metric("train_f1", train_report["weighted avg"]["f1-score"])
            mlflow.log_metric("val_f1", val_report["weighted avg"]["f1-score"])
            mlflow.log_metric("test_f1", test_report["weighted avg"]["f1-score"])

            mlflow.log_metric("train_precision", train_report["weighted avg"]["precision"])
            mlflow.log_metric("val_precision", val_report["weighted avg"]["precision"])
            mlflow.log_metric("test_precision", test_report["weighted avg"]["precision"])

            mlflow.log_metric("train_recall", train_report["weighted avg"]["recall"])
            mlflow.log_metric("val_recall", val_report["weighted avg"]["recall"])
            mlflow.log_metric("test_recall", test_report["weighted avg"]["recall"])

            if val_report["weighted avg"]["f1-score"] > best_f1:
                best_f1 = val_report["weighted avg"]["f1-score"]
                best_run_id = run.info.run_id

    # Registrar el mejor modelo como 'best_model' y ponerlo en producción
    model_uri = f"runs:/{best_run_id}/model"
    mlflow.register_model(model_uri, MODEL_NAME)

    client = mlflow.tracking.MlflowClient()
    versions = client.get_latest_versions(MODEL_NAME, stages=["None"])
    if versions:
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=versions[0].version,
            stage="Production",
            archive_existing_versions=True
        )

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id="train_cover_type_rf_model",
    default_args=default_args,
    description="Entrena RF para Cover_Type con preprocesamiento y F1-score, y lo registra en MLflow",
    schedule_interval=None,
    start_date=datetime(2025, 4, 4),
    catchup=False,
    tags=["training", "mlflow", "cover_type"]
) as dag:

    train_model_task = PythonOperator(
        task_id="train_and_register_model",
        python_callable=train_and_register_model
    )

    train_model_task
