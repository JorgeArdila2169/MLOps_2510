from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import mlflow
from mlflow.tracking import MlflowClient
import os

def promote_best_model_with_tag():
    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
    experiment_name = "diabetes_prediction_rf"

    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    experiment_id = experiment.experiment_id

    # Buscar el mejor run
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["metrics.test_f1 DESC"]
    )

    if not runs:
        print("No hay runs completados.")
        return

    best_run = runs[0]
    best_run_id = best_run.info.run_id
    best_f1 = best_run.data.metrics.get("test_f1", None)

    if best_f1 is None:
        print("Mejor run sin test_f1.")
        return

    print(f"Marcando run {best_run_id} como best_model con test_f1={best_f1:.4f}")

    # Limpiar tags "best_model" anteriores
    for run in runs:
        if run.data.tags.get("best_model") == "true":
            client.set_tag(run.info.run_id, "best_model", "false")

    # Asignar tag al mejor
    client.set_tag(best_run_id, "best_model", "true")

    print(f"Run {best_run_id} marcado exitosamente como best_model=True.")

default_args = {'start_date': datetime(2025, 5, 5)}

with DAG('promote_best_model_with_tag',
         schedule_interval=None,
         default_args=default_args,
         catchup=False) as dag:

    promote_task = PythonOperator(
        task_id='promote_best_model_task',
        python_callable=promote_best_model_with_tag
    )
