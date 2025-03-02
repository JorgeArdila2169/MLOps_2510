
import tensorflow_transform as tft

# Definir las características numéricas y categóricas
NUMERIC_FEATURES = [
    "Elevation", "Hillshade_9am", "Hillshade_Noon", "Horizontal_Distance_To_Fire_Points",
    "Horizontal_Distance_To_Hydrology", "Horizontal_Distance_To_Roadways", "Slope",
    "Vertical_Distance_To_Hydrology"
]

CATEGORICAL_FEATURES = ["Soil_Type", "Wilderness_Area"]

LABEL_KEY = "Cover_Type"

# Función para renombrar las características transformadas
def transformed_name(key):
    return key + "_xf"

# Función de preprocesamiento para TFX
def preprocessing_fn(inputs):
    outputs = {}
    
    # Aplicar Z-score a las características numéricas
    for feature in NUMERIC_FEATURES:
        outputs[transformed_name(feature)] = tft.scale_to_z_score(inputs[feature])
    
    # Mapear variables categóricas a índices enteros
    for feature in CATEGORICAL_FEATURES:
        outputs[transformed_name(feature)] = tft.compute_and_apply_vocabulary(inputs[feature])
    
    # Transformar la variable objetivo
    outputs[transformed_name(LABEL_KEY)] = tft.compute_and_apply_vocabulary(inputs[LABEL_KEY])

    return outputs
