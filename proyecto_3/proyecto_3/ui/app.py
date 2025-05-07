import gradio as gr
import requests
import os

FASTAPI_PREDICT_URL = os.environ.get('FASTAPI_PREDICT_URL', 'http://fastapi:8000/predict')

def predict(num_lab_procedures, num_medications, time_in_hospital, number_inpatient, A1Cresult):
    input_data = [{
        "num_lab_procedures": num_lab_procedures,
        "num_medications": num_medications,
        "time_in_hospital": time_in_hospital,
        "number_inpatient": number_inpatient,
        "A1Cresult": A1Cresult
    }]
    
    response = requests.post(FASTAPI_PREDICT_URL, json={"data": input_data})
    if response.status_code != 200:
        return f"Error: {response.text}"
    
    res_json = response.json()
    pred = res_json["predictions"][0]
    model_info = res_json["model_info"]
    
    return f"Predicción: {pred}\nModelo: {model_info['run_id']} (tag: {model_info['tag']})"

iface = gr.Interface(
    fn=predict,
    inputs=[
        gr.Number(label="Número de procedimientos de laboratorio", value=40),
        gr.Number(label="Número de medicamentos", value=5),
        gr.Number(label="Tiempo en hospital (días)", value=3),
        gr.Number(label="Número de hospitalizaciones previas", value=1),
        gr.Dropdown(choices=['None', 'Norm', '>7', '>8'], label="Resultado A1C", value='None')
    ],
    outputs="text",
    title="Interfaz de Predicción de Diabetes",
    description="Usando el modelo marcado como 'best_model' por la API"
)

iface.launch(server_name="0.0.0.0", server_port=8503)
