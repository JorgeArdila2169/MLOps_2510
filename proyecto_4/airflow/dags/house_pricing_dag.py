from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime
import requests
import pandas as pd
import numpy as np
import mlflow
import shap
import os
import sqlalchemy
import random
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error, r2_score
import matplotlib.pyplot as plt

# Configuración global
API_URL = "http://10.43.101.108:80/data"
GROUP = 5
DAY = "Wednesday"
RAW_TABLE = "raw_data"
CLEAN_TABLE = "clean_data"

# DAG
default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'retries': 0
}

dag = DAG(
    'house_pricing_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=True
)

def get_mysql_engine():
    user = os.environ['DATA_MYSQL_USER']
    password = os.environ['DATA_MYSQL_PASSWORD']
    host = os.environ['DATA_MYSQL_HOST']
    db = os.environ['DATA_MYSQL_DATABASE']
    port = os.environ.get('DATA_MYSQL_PORT', 3306)
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    return sqlalchemy.create_engine(connection_string)

def request_data():
    print("Iniciando solicitud de datos a la API...")
    params = {"group_number": GROUP, "day": DAY}
    response = requests.get(API_URL, params=params, timeout=60)

    if response.status_code == 400:
        print("No hay más datos disponibles en la API. DAG finaliza exitosamente.")
        return False

    json_data = response.json()
    data = json_data.get('data', [])
    api_batch_number = json_data.get("batch_number", None)

    if not data:
        print("No se recibió información en la respuesta.")
        return False

    df = pd.DataFrame(data)

    engine = get_mysql_engine()
    try:
        result = pd.read_sql(f"SELECT MAX(batch_number) AS max_batch FROM {RAW_TABLE}", con=engine)
        db_batch_number = result['max_batch'][0]
        next_batch = int(db_batch_number) + 1 if pd.notna(db_batch_number) else 0
    except Exception as e:
        print("Error al obtener el último batch_number:", e)
        next_batch = 0

    df['batch_number'] = api_batch_number if api_batch_number is not None else next_batch
    print(f"Guardando batch {df['batch_number'].iloc[0]} con {len(df)} registros.")
    df.to_sql(RAW_TABLE, con=engine, if_exists='append', index=False)
    print("Datos crudos almacenados en la base de datos exitosamente.")
    return True

def validate_batch():
    print("Validando condiciones para reentrenar el modelo...")
    engine = get_mysql_engine()
    batch_df = pd.read_sql(f"SELECT MAX(batch_number) AS max_batch FROM {RAW_TABLE}", con=engine)
    last_batch = batch_df['max_batch'][0]

    if last_batch is None:
        print("No hay ningún batch registrado aún.")
        return True

    if last_batch == 0:
        print("Primer batch detectado (batch 0). Se entrenará el primer modelo base.")
        return True

    current_df = pd.read_sql(f"SELECT * FROM {RAW_TABLE} WHERE batch_number = {last_batch}", con=engine)
    current_std = current_df['price'].std()

    previous_df = pd.read_sql(f"SELECT * FROM {RAW_TABLE} WHERE batch_number = {last_batch - 1}", con=engine)
    previous_std = previous_df['price'].std()

    condition_size = len(current_df) >= 50000
    condition_drift = previous_std is not None and abs(current_std - previous_std) / previous_std >= 0.25

    if condition_size and condition_drift:
        print("Se cumple la condición de tamaño y drift, se entrenará el modelo.")
        return True
    elif condition_size:
        print("Solo se cumple la condición de tamaño >= 50000, se entrenará el modelo.")
        return True
    elif condition_drift:
        print("Solo se cumple la condición de drift >= 25%, se entrenará el modelo.")
        return True
    else:
        print("No se cumple ninguna condición para reentrenar. DAG finalizará sin errores.")
        return False

def preprocess_data():
    print("Iniciando preprocesamiento de datos...")
    engine = get_mysql_engine()
    df = pd.read_sql(f"SELECT * FROM {RAW_TABLE}", con=engine)
    df = df.drop(columns=['batch_number', 'street', 'state', 'city', 'prev_sold_date', 'status', 'brokered_by'])
    df = df[df['price'] > 1000]  # Filtrar precios muy bajos
    df.dropna(inplace=True)
    df.to_sql(CLEAN_TABLE, con=engine, if_exists='replace', index=False)
    print("Datos preprocesados guardados en clean_data exitosamente.")

def train_models():
    print("Entrenando modelos Gradient Boosting...")
    engine = get_mysql_engine()
    df = pd.read_sql(f"SELECT * FROM {CLEAN_TABLE}", con=engine)
    X = df.drop(columns=['price'])
    y = df['price']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
    mlflow.set_experiment("house_price_regression")

    for i in range(3):
        X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        n_estimators = random.randint(100, 300)
        learning_rate = random.uniform(0.01, 0.1)
        max_depth = random.randint(3, 7)

        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=42
        )
        with mlflow.start_run(run_name=f"GBR_{i+1}") as run:
            mlflow.sklearn.autolog()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            rmse = mean_squared_error(y_val, y_pred, squared=False)
            mae = mean_absolute_error(y_val, y_pred)
            mape = mean_absolute_percentage_error(y_val, y_pred)
            r2 = r2_score(y_val, y_pred)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("mae", mae)
            mlflow.log_metric("mape", mape)
            mlflow.log_metric("r2", r2)
            print(f"Run GBR_{i+1} registrado: n_estimators={n_estimators}, lr={learning_rate:.3f}, depth={max_depth}, RMSE={rmse:.2f}, MAPE={mape:.4f}, R2={r2:.3f}")

def tag_best_model():
    print("Promoviendo mejor modelo a producción...")
    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("house_price_regression")
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.mae ASC"],
        filter_string="attributes.status = 'FINISHED'"
    )

    if not runs:
        print("No hay runs para evaluar.")
        return

    # Eliminar tags anteriores
    for run in runs:
        if run.data.tags.get("stage") == "best_model":
            print(f"Removiendo tag 'best_model' de run {run.info.run_id}")
            client.set_tag(run.info.run_id, "stage", "archived")

    best_run_id = runs[0].info.run_id
    client.set_tag(best_run_id, "stage", "best_model")
    print(f"Run {best_run_id} etiquetado como best_model exitosamente.")

def shap_explanation():
    print("Generando explicación SHAP del mejor modelo...")
    import tempfile
    engine = get_mysql_engine()
    df = pd.read_sql(f"SELECT * FROM {CLEAN_TABLE}", con=engine)
    X = df.drop(columns=['price'])

    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("house_price_regression")
    runs = client.search_runs(experiment_ids=[experiment.experiment_id], filter_string="tags.stage = 'best_model'", order_by=["start_time DESC"], max_results=1)
    best_model_uri = f"runs:/{runs[0].info.run_id}/model"
    model = mlflow.sklearn.load_model(best_model_uri)

    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)
    shap.summary_plot(shap_values, X, show=False)

    tmp_path = "/tmp/shap_summary.png"
    plt.savefig(tmp_path)
    mlflow.log_artifact(tmp_path, artifact_path="shap")
    print("Explicación SHAP generada y registrada como 'shap/shap_summary.png'.")


# DAG tasks
t1 = ShortCircuitOperator(task_id="request_data", python_callable=request_data, dag=dag)
t2 = ShortCircuitOperator(task_id="validate_batch", python_callable=validate_batch, dag=dag)
t3 = PythonOperator(task_id="preprocess_data", python_callable=preprocess_data, dag=dag)
t4 = PythonOperator(task_id="train_models", python_callable=train_models, dag=dag)
t5 = PythonOperator(task_id="tag_best_model", python_callable=tag_best_model, dag=dag)
t6 = PythonOperator(task_id="shap_explanation", python_callable=shap_explanation, dag=dag)

# DAG orden
t1 >> t2 >> t3 >> t4 >> t5 >> t6
