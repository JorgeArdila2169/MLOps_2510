## PROYECTO 3
## Nivel 3
## Kubernetes

## DESCRIPCIÓN

Este proyecto implementa una arquitectura MLOps completa desplegada sobre una única máquina virtual actuando como clúster Kubernetes, permitiendo la automatización y orquestación de un sistema de Machine Learning end-to-end. El objetivo es facilitar un flujo continuo desde la recolección de datos hasta el monitoreo y escalamiento de la inferencia, simulando un entorno de producción realista. Se utilizó Docker y Kubernetes para aplicar la filosofía de contenedores en cada componente, asegurando modularidad y replicabilidad.

## OBJETIVOS DEL PROYECTO

•	Automatizar el flujo completo de un sistema de machine learning con MLOps utilizando herramientas de nivel industrial.

•	Ejecutar procesos periódicos de entrenamiento utilizando DAGs de Airflow.

•	Registrar los resultados de cada ejecución en MLflow, incluyendo hiperparámetros, métricas, artefactos y versiones de modelo.

•	Usar MLflow para gestionar versiones de modelo y designar automáticamente el mejor como "Production".

•	Proveer una API RESTful y una interfaz gráfica que permitan consumir el modelo de producción sin necesidad de cambios en el código.

•	Establecer un sistema de monitoreo y observabilidad con Prometheus y Grafana.

•	Simular carga y estimar la capacidad máxima de usuarios concurrentes mediante Locust.

## ESTRUCTURA DEL PROYECTO

La estructura del repositorio se diseñó para facilitar el despliegue modular de cada componente. Cada carpeta contiene los scripts y archivos necesarios para ejecutar su respectivo servicio.

![basic train flow](img/01_estructura.png)



## FLUJO DE TRABAJO MLOPS


### 1. Recolección y Procesamiento de Datos

Se crearon múltiples DAGs en Airflow para automatizar la ingesta y transformación de los datos:

•	load_raw_data.py: Carga progresiva en lotes de 15.000 registros a la base de datos RAW.
•	process_data.py: Limpieza, transformación y escritura en la base CLEAN.
•	load_val_test_data.py: Divide los datos procesados en conjuntos de entrenamiento, validación y prueba.

Cada ejecución se encuentra agendada y puede ser monitoreada desde la interfaz de Airflow.


### 2. Entrenamiento y Registro de Modelos

•	Los modelos se entrenan usando el DAG train_model.py.
•	Se registra cada ejecución en MLflow, incluyendo:
o	AUC, Precisión, Recall.
o	Artefactos como el modelo serializado (.pkl) y gráficas de evaluación.
•	El mejor modelo (por AUC) se promueve automáticamente a "Production" usando el DAG promote_best_model.py, desde el cual se etiqueta (TAG) con ‘true’ en el campo ‘best_model’ aquel modelo que posee el mejor rendimiento (accuracy).
•	
MLflow está configurado con PostgreSQL para los metadatos y MinIO como bucket S3 para artefactos.

### 3. API para Inferencia (FastAPI)

•	Implementada en un contenedor independiente.
•	Expone dos endpoints:
o	/predict: Recibe datos, consulta a MLflow el modelo en producción y retorna la predicción.
o	/metrics: Expuesto para Prometheus. Incluye latencia, conteo de peticiones y errores.

El código es genérico y el modelo activo se selecciona mediante mlflow.pyfunc.load_model("models:/Model/Production"), lo que elimina la necesidad de actualizaciones manuales del código al cambiar de versión.



### 4. Interfaz de usuario (UI) con Streamlit


•	Construida para facilitar el ingreso de valores por parte del usuario.
•	Permite probar rápidamente predicciones y ver qué versión de modelo fue usada.
•	El archivo ui/app.py contiene el código de la interfaz, que se conecta con la API de FastAPI.


### 5. Observabilidad


•	Prometheus recolecta métricas expuestas por FastAPI (tiempo de respuesta, volumen, errores).
•	Grafana despliega dashboards personalizados para:
o	Latencia promedio.
o	Tráfico por minuto.
o	Errores por tipo de petición.
•	Configuración de dashboards en grafana/provisioning/.



### 6. Pruebas de Carga


Con Locust se simularon diferentes escenarios de usuarios concurrentes atacando el endpoint /predict.

Se midieron los siguientes KPIs:
-	RPS (requests per second)
-	Tiempo promedio de respuesta
-	Porcentaje de errores
-	Capacidad máxima sostenible antes de superar 20% de errores

## EVIDENCIAS DE LOCUST

•	Se ejecutaron cargas crecientes de 15, 25, 35, 50 y hasta 100 usuarios concurrentes.

![basic train flow](img/02_locust.png)

A partir de la gráfica anterior, se evidencia que:

•	Rendimiento por segundo: el sistema fue capaz de mantener una tasa estable de 10-13 peticiones por segundo sin errores reportados (línea verde, sin puntos rojos).
•	Tiempo de respuesta:
o	La mediana (50th percentile) se mantuvo generalmente por debajo de los 3000 ms.
o	El 95th percentile presentó picos, pero en los rangos operativos bajos (hasta 25 usuarios) los tiempos fueron aceptables.
•	Número de usuarios: el sistema operó sin fallos hasta los 25 usuarios concurrentes, presentando tiempos de respuesta razonables y constantes.

Conclusión técnica: El sistema es estable y confiable hasta un máximo de 25 usuarios concurrentes, sin errores ni caídas del contenedor. Los tiempos de respuesta se mantuvieron por debajo de los 3 segundos incluso bajo esa carga. Más allá de ese umbral, comienzan a observarse incrementos significativos en la latencia y potenciales errores, por lo que se recomienda ajustar los recursos o escalar horizontalmente si se espera una mayor concurrencia.



## TECNOLOGÍAS Y SERVICIOS

Este ecosistema se construyó tomando como referencia el diagrama propuesto en el encunciado del proyecto, para lo cual, se usaron las siguientes herramientas:

•	Kubernetes sobre VM: cluster de un nodo ejecutado sobre una máquina virtual.
•	Docker Compose: para pruebas locales.
•	Apache Airflow: automatización de workflows y DAGs.
•	MLflow + MinIO + PostgreSQL: experiment tracking, gestión de modelos y artefactos.
•	FastAPI: API REST de inferencia.
•	Streamlit: interfaz gráfica de usuario.
•	Prometheus + Grafana: monitoreo y dashboards.
•	Locust: pruebas de carga y rendimiento.



## SEGUIMIENTO Y MÉTRICAS


•	MLflow UI: http://localhost:5000
•	Grafana: http://localhost:3000 (usuario: admin / contraseña: admin)
•	Locust: http://localhost:8089

Cada experimento registrado puede visualizarse con sus respectivos parámetros, métricas y artefactos.


### CONCLUSIÓN

Este proyecto representa una implementación robusta de una arquitectura MLOps moderna, con todas las etapas del ciclo de vida (end-to-end) de un modelo de ML integradas de forma automática y observable. El uso de una única VM simula un entorno de despliegue económico y reproducible para escenarios académicos o prototipos profesionales. La modularidad y el uso de estándares abiertos aseguran portabilidad y escalabilidad futura. La inclusión de métricas, monitoreo y pruebas de carga posiciona esta solución como lista para producción en ambientes controlados.


### VIDEO DE SUSTENTACIÓN

En el siguiente enlace se incluye el video mediante el cual se sustenta el proyecto:

https://www.youtube.com/watch?v=-WlYubfFD9E


### REFERENCIAS

•	Airflow: https://airflow.apache.org/
•	MLflow: https://mlflow.org/
•	Streamlit: https://streamlit.io/
•	Prometheus: https://prometheus.io/
•	Grafana: https://grafana.com/
•	Locust: https://locust.io/
•	Dataset: https://doi.org/10.24432/C5230J




### EJECUCIÓN DEL PROYECTO

El proyecto quedó montado completamente en la máquina virtual con dirección ip: 10.43.101.165

El despliegue se realizó en una máquina virtual con K3s. Los manifiestos YAML fueron definidos para cada componente.

Requisitos:
•	Docker
•	Docker Compose
•	Kubernetes (K3s o Minikube)

Para el despliegue local, se ejecuta el siguiente comando para construir e iniciar todos los servicios:

$ docker-compose up --build 

Para el despliegue en Kubernetes, se ejecuta el siguiente comando para instalar microk8s en una sola máquina virtual:

sudo snap install microk8s --classic

sudo microk8s enable dns storage ingress

Luego, se ejecuta el siguiente comando, con la finalidad de aplicar manifiestos YAML desde la carpeta k8s/:

kubectl apply -f "nombre-del-archivo.yaml"

Acceder a la inferencia y dashboards a través de NodePort o Ingress.

### Acceso:
•	MLflow UI: http://:5000
•	API FastAPI: http://:8000
•	Streamlit UI: http://:8501
•	Grafana: http://:3000 (admin/admin)
•	Locust: http://:8089

