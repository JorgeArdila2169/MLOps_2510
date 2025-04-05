import gradio as gr
import requests
import os

# URL de la API
inference_api_uri = os.getenv("INFERENCE_API_URI", "http://fastapi:8000/predict/")

def predict(
    Elevation,
    Hillshade_9am,
    Hillshade_Noon,
    Horizontal_Distance_To_Fire_Points,
    Horizontal_Distance_To_Hydrology,
    Horizontal_Distance_To_Roadways,
    Slope,
    Vertical_Distance_To_Hydrology,
    Soil_Type,
    Wilderness_Area
):
    payload = {
        "Elevation": Elevation,
        "Hillshade_9am": Hillshade_9am,
        "Hillshade_Noon": Hillshade_Noon,
        "Horizontal_Distance_To_Fire_Points": Horizontal_Distance_To_Fire_Points,
        "Horizontal_Distance_To_Hydrology": Horizontal_Distance_To_Hydrology,
        "Horizontal_Distance_To_Roadways": Horizontal_Distance_To_Roadways,
        "Slope": Slope,
        "Vertical_Distance_To_Hydrology": Vertical_Distance_To_Hydrology,
        "Soil_Type": Soil_Type,
        "Wilderness_Area": Wilderness_Area,
    }

    try:
        response = requests.post(inference_api_uri, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result.get("prediction", "Sin predicción")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Excepción: {e}"

# Interfaz con tema oscuro
with gr.Blocks(theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("# Clasificador de Cobertura Vegetal", elem_id="title")
    gr.Markdown("Predecimos el tipo de terreno a partir de datos topográficos usando Random Forest")
    with gr.Row():
        with gr.Column():
            Elevation = gr.Number(label="Elevation")
            Hillshade_9am = gr.Number(label="Hillshade 9am")
            Hillshade_Noon = gr.Number(label="Hillshade Noon")
            Horizontal_Distance_To_Fire_Points = gr.Number(label="Distancia al fuego (Horizontal)")
            Horizontal_Distance_To_Hydrology = gr.Number(label="Distancia a hidrología (Horizontal)")
            Horizontal_Distance_To_Roadways = gr.Number(label="Distancia a carreteras (Horizontal)")
            Slope = gr.Number(label="Slope")
            Vertical_Distance_To_Hydrology = gr.Number(label="Distancia vertical a hidrología")

            Soil_Type = gr.Textbox(label="Soil Type", placeholder="Ej: C4703")
            Wilderness_Area = gr.Textbox(label="Wilderness Area", placeholder="Ej: Commanche")

        with gr.Column():
            output = gr.Textbox(label="Resultado")

    btn = gr.Button("Predecir")
    btn.click(
        fn=predict,
        inputs=[
            Elevation, Hillshade_9am, Hillshade_Noon,
            Horizontal_Distance_To_Fire_Points,
            Horizontal_Distance_To_Hydrology,
            Horizontal_Distance_To_Roadways,
            Slope,
            Vertical_Distance_To_Hydrology,
            Soil_Type,
            Wilderness_Area
        ],
        outputs=output
    )

demo.launch(server_name="0.0.0.0", server_port=8503)
