## Taller MLflow:

## DESCRIPCIÓN

En este taller, se implementó un flujo completo de MLOps utilizando MLflow, PostgreSQL, MinIO y JupyterLab. Se abordaron las etapas fundamentales de un pipeline de machine learning, desde la gestión de datos hasta el despliegue de una API de inferencia basada en un modelo entrenado.

El objetivo principal del taller fue construir una infraestructura escalable para el entrenamiento y la gestión de modelos, asegurando la trazabilidad de los experimentos y la reproducibilidad de los resultados. 

Lo anterior, se traduce en la implementación de un flujo (pipeline) de MLOps para la gestión, experimentación, almacenamiento y despliegue de modelos de machine learning con MLflow.

## ESTRUCTURA DEL PROYECTO

![basic train flow](img/01_arquitectura.png)


Este taller emplea los siguientes servicios:

-	PostgreSQL: Bases de datos para almacenar los datos de pingüinos en bruto y procesados.

-	MLflow: Plataforma de gestión de experimentos y almacenamiento de modelos.

-	MinIO: Almacenamiento de artefactos de modelos para MLflow.

-	JupyterLab: Desarrollo de un pipeline de entrenamiento y análisis de experimentos.

-	FastAPI: Exposición de un endpoint para realizar inferencia utilizando modelos registrados en MLflow.

-	Docker y Docker Compose: Orquestación de los servicios en contenedores.


## IMPLEMENTACIÓN DEL TALLER

Para la implementación del taller se creó un archivo docker-compose.yaml, el cual define una infraestructura basada en contenedores que contiene los servicios necesarios como, PostgreSQL (para la base de datos) y MinIO (para almacenar modelos y artefactos). El puerto 5433 fue configurado para PostgreSQL, y para MinIO en el puerto 9000 y su interfaz web en 9001.

### Configuración del Entorno
Se inició la configuración del entorno con la instalación de Docker y la clonación del repositorio del taller.
git clone <repositorio>
cd taller_mlflow
Se levantaron los servicios necesarios con Docker Compose:
docker-compose up -d --build

### Creación de Bases de Datos en PostgreSQL
Se accedió al contenedor de PostgreSQL para crear las bases de datos necesarias:

docker exec -it postgres_mlops psql -U mlflowuser

Uno de los retos a los que se enfrentó el equipo de trabajo fue en la creación de las bases de datos, porque después de investigar, se logró determinar que era necesario ejecutar en la consola de PostgreSQL, los siguientes comandos:

CREATE DATABASE raw_data;
CREATE DATABASE processed_data;

### Configuración y Despliegue de MLflow

Se ejecutó MLflow con PostgreSQL como backend y MinIO como almacenamiento de artefactos:
mlflow server --backend-store-uri postgresql://mlflowuser:mlflowpassword@localhost:5433/mlflow_db \
             		 --default-artifact-root s3://mlflow-artifacts/ \
              		--host 0.0.0.0 --port 5000

MLflow quedó accesible en http://localhost:5000


### Entrenamiento y Registro del Modelo

Se utilizó JupyterLab para crear y ejecutar el notebook penguins_experiments.ipynb, el cual:

•	Carga los datos brutos desde PostgreSQL.
•	Entrena el modelo clasificador utilizando el algoritmo Random Forest, con distintas configuraciones tomando los hiperparámetros de manera aleatoria.
•	Registra los modelos y métricas en MLflow.

En la siguiente imagen se evidencia que los modelos entrenados estaban siendo registrados en MLflow, para el caso particular, se configuró el notebook para entrenar 20 modelos:

![basic train flow](img/02_Experimentos.png)

El mejor modelo se registró en MLflow con la etiqueta Production (Tag: Champion). En este aspecto, el equipo encontró que la versión de la interfaz de usuario de MLflow que se utilizó para la elaboración del presente taller, no posee la opción para cambiar el estado (stage) del modelo. Por lo tanto, se optó por la alternativa de hacerlo a través de código dentro el notebook, como se observa en la siguiente imagen.

![basic train flow](img/03_Stage_Modelo.png)


### Implementación de la API de inferencia


La API de inferencia fue desarrollada con FastAPI (api/main.py) para gestionar solicitudes de predicción mediante el modelo con mejores métricas de los 20 modelos previamente entrenados y registrados MLflow. Este modelo se diseñó para generar inferencias a partir de los datos de entrada. La implementación se basa en la entrega previa del taller de API.

Para levantar la API, se ejecutó:

Para la inferencia del modelo (FastAPI): http://localhost:8000/docs 


### Inferencia de Datos

Las entradas deben ser introducidas manualmente por el usuario y de allí se realiza la predicción mediante el modelo Random Forest registrado como el mejor del resto. Los datos de entrada que se requieren son: Tamaño (mm) y grosor del pico (mm), a la longitud de la aleta (mm) y al peso del animal (gramos). La imagen a continuación, permite observar la interfaz de la API para el ingreso de los datos de entrada que serán utilizados para el modelo para realizar la respectiva inferencia:

![basic train flow](img/04_Prediction.png)

## RESUMEN DEL FLUJO DE TRABAJO IMPLEMENTADO

1. Configuración del entorno
2. Levantamiento de servicios con Docker
3. Creación de bases de datos en PostgreSQL
4. Configuración y despliegue de MLflow
5. Entrenamiento de modelos en JupyterLab
6. Registro del mejor modelo en MLflow
7. Desarrollo de la API de inferencia
8. Pruebas de predicción con la API

Finalmente, para acceder a los servicios y ejecutar la solución del taller implementada, se recomienda usar las siguientes URL’s:

MinIO está disponible en http://localhost:9001
Usuario: admin ; Contraseña: supersecret

MLflow UI: http://localhost:5000

PostgreSQL: Disponible en localhost:5433

Interfaz de Airflow (Airflow UI): http://localhost:8080/ 
Usuario: airflow ; Contraseña: airflow

Para la inferencia del modelo (FastAPI): http://localhost:8000/docs 


