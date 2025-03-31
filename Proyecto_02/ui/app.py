# ui/app.py

import streamlit as st
import requests
import json

st.set_page_config(page_title="Inferencia Forest Cover", layout="centered")
st.title("Predicción de Tipo de Cobertura Forestal")

st.markdown("Ingrese las características del terreno para predecir el tipo de cobertura forestal.")

# Crear inputs dinámicamente (por simplicidad se piden solo los primeros atributos)
elevation = st.number_input("Elevación (m)", min_value=0, max_value=5000, value=2000)
aspect = st.slider("Orientación (°)", 0, 360, 180)
slope = st.slider("Pendiente (°)", 0, 90, 10)
horz_dist_hydro = st.number_input("Distancia horizontal al agua (m)", value=100)
vert_dist_hydro = st.number_input("Distancia vertical al agua (m)", value=50)
horz_dist_road = st.number_input("Distancia a carretera (m)", value=300)
hillshade_9am = st.slider("Iluminación 9am", 0, 255, 150)
hillshade_noon = st.slider("Iluminación mediodía", 0, 255, 200)
hillshade_3pm = st.slider("Iluminación 3pm", 0, 255, 100)
horz_dist_fire = st.number_input("Distancia a puntos de fuego (m)", value=400)

# Placeholder para binarios: wilderness_area y soil_type
wilderness = [0, 1, 0, 0]  # ejemplo: sólo el segundo activo
soil = [0]*40
soil[10] = 1  # ejemplo: soil_type 10 activo

input_features = [
    elevation, aspect, slope,
    horz_dist_hydro, vert_dist_hydro, horz_dist_road,
    hillshade_9am, hillshade_noon, hillshade_3pm,
    horz_dist_fire
] + wilderness + soil

if st.button("Predecir cobertura"):
    try:
        response = requests.post(
            "http://fastapi:80/predict",
            json={"features": input_features}
        )
        if response.status_code == 200:
            result = response.json()
            st.success(f"Tipo de cobertura forestal predicho: {result['prediction'][0]}")
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(f"Excepción durante la predicción: {e}")
