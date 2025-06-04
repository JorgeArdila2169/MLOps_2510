import gradio as gr
import requests
import os
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
import matplotlib.pyplot as plt
import base64
from io import BytesIO

FASTAPI_PREDICT_URL = os.environ.get('FASTAPI_PREDICT_URL', 'http://10.43.101.165:30800/predict')
MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://10.43.101.165:30500')

# Función para hacer inferencia con FastAPI
def predict(bed, bath, acre_lot, zip_code, house_size):
    input_data = [{
        "bed": bed,
        "bath": bath,
        "acre_lot": acre_lot,
        "zip_code": zip_code,
        "house_size": house_size
    }]
    try:
        response = requests.post(FASTAPI_PREDICT_URL, json={"data": input_data})
        response.raise_for_status()
        res_json = response.json()
        pred = res_json["predictions"][0]
        model_info = res_json["model_info"]
        return f"Predicción de precio: ${pred:,.2f}\nModelo: {model_info['run_id']} (tag: {model_info['tag']})"
    except Exception as e:
        return f"Error: {e}"

# Función para cargar historial de runs de MLflow
def load_history():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()
    experiment = client.get_experiment_by_name("house_price_regression")
    runs = client.search_runs([experiment.experiment_id], order_by=["start_time DESC"])
    rows = []
    for run in runs:
        tags = run.data.tags
        status = "best_model" if tags.get("stage") == "best_model" else "descartado"
        row = {
            "Run ID": run.info.run_id,
            "Status": status,
            "RMSE": run.data.metrics.get("rmse"),
            "MAE": run.data.metrics.get("mae"),
            "MAPE": run.data.metrics.get("mape"),
            "R2": run.data.metrics.get("r2")
        }
        rows.append(row)
    return pd.DataFrame(rows)

# Función para mostrar la imagen SHAP (previamente registrada en MLflow)
def load_shap_image():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()
    experiment = client.get_experiment_by_name("house_price_regression")
    runs = client.search_runs([experiment.experiment_id], filter_string="tags.stage = 'best_model'", order_by=["start_time DESC"], max_results=1)
    run_id = runs[0].info.run_id
    artifact_url = f"{runs[0].info.artifact_uri}/shap/"
    try:
        img_path = f"/tmp/shap_{run_id}.png"
        response = requests.get(f"{artifact_url}shap_summary.png", stream=True)
        with open(img_path, 'wb') as f:
            f.write(response.content)
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Interfaz principal
with gr.Blocks() as demo:
    gr.Markdown("# Inferencia del modelo de precios de casas")

    with gr.Row():
        bed = gr.Number(label="Número de habitaciones", value=3)
        bath = gr.Number(label="Número de baños", value=2)
        acre_lot = gr.Number(label="Tamaño del lote (acres)", value=0.25)
        zip_code = gr.Number(label="Código postal", value=10001)
        house_size = gr.Number(label="Tamaño de la casa (pies cuadrados)", value=1800)
    
    with gr.Row():
        output = gr.Textbox(label="Resultado de inferencia")
        btn = gr.Button("Predecir")
        btn.click(predict, inputs=[bed, bath, acre_lot, zip_code, house_size], outputs=output)

    gr.Markdown("## Historial de modelos")
    history = gr.Dataframe(load_history())

    gr.Markdown("## Interpretabilidad - SHAP")
    shap_image = load_shap_image()
    if shap_image:
        gr.Image(value=f"data:image/png;base64,{shap_image}", label="Gráfico SHAP")
    else:
        gr.Textbox(value="No se encontró artefacto SHAP registrado en MLflow")

    gr.Markdown("---")
    gr.Textbox(value="Powered by MLOps Final Project", interactive=False)

# Lanzamiento
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8503)

