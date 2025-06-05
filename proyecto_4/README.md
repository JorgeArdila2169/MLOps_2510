# Proyecto Final: Predicción de Precios de Vivienda

## Descripción General

Este proyecto implementa un sistema de MLOps completo de predicción de precios de vivienda. Se automatizan las fases de ingesta, procesamiento, entrenamiento, despliegue y monitoreo del modelo mediante un entorno orquestado con Kubernetes, Airflow, MLflow, FastAPI, Gradio, Prometheus, Grafana y Argo CD

## Arquitectura General

```
+---------------------+        +----------------+       +-----------------+       +----------------+
|     Airflow DAG     +------->+  Procesamiento  +------>+ Entrenamiento    +------>+   MLflow       |
+---------------------+        +----------------+       +-----------------+       +----------------+
       |                        |                        |                           |
       v                        v                        v                           v
  Ingesta API           Limpieza & División       Modelos Regresores         Registro Experimentos
       |                                                                        + SHAP Explanation
       v
+---------------------+
|  FastAPI de Inferencia |
+---------------------+
       |
       v
+---------------------+
|     Interfaz Gradio    |
+---------------------+
       |
       v
+---------------------+
|   Dashboards Grafana   |<--- Prometheus
+---------------------+
```

## Directorio y archivos del proyecto

```
.github/workflows/proyecto_4.yml
proyecto_4/
├── airflow
│   ├── dags
│   │   └── house_pricing_dag.py
│   ├── Dockerfile
│   ├── logs
│   └── plugins
├── analysis
│   ├── analyze.py
│   ├── batch_0_raw.json
│   ├── batch_1_raw.json
│   ├── batch_2_raw.json
│   ├── batch_3_raw.json
│   ├── batch_4_raw.json
│   ├── batch_5_raw.json
│   ├── get_data.py
│   └── test_api.py
├── api
│   ├── Dockerfile
│   └── main.py
├── argo-application.yaml
├── Dockerfile.mlflow
├── k8s
│   ├── airflow
│   │   ├── airflow-data-pvc.yaml
│   │   ├── airflow-init-job.yaml
│   │   ├── airflow-logs-pvc.yaml
│   │   ├── airflow-scheduler.yaml
│   │   ├── airflow-triggerer.yaml
│   │   ├── airflow-webserver.yaml
│   │   ├── airflow-worker.yaml
│   │   ├── postgres.yaml
│   │   └── redis.yaml
│   ├── fastapi
│   │   └── fastapi.yaml
│   ├── gradio
│   │   └── gradio.yaml
│   ├── grafana
│   │   ├── dashboard_config.yaml
│   │   ├── dashboard_json.yaml
│   │   ├── datasource_config.yaml
│   │   └── grafana.yaml
│   ├── kustomization.yaml
│   ├── minio
│   │   └── minio.yaml
│   ├── mlflow
│   │   └── mlflow.yaml
│   ├── mysql-data
│   │   └── mysql-data.yaml
│   ├── mysql-mlflow
│   │   └── mysql-mlflow.yaml
│   ├── project-secrets.yaml
│   └── prometheus
│       └── prometheus.yaml
└── ui
    ├── app.py
    └── Dockerfile
```

## Componentes del Proyecto

### 1. `airflow/`

* `house_pricing_dag.py`: DAG que realiza el ciclo completo cada 15 min
* Ejecuta:

  * Ingesta de datos desde API
  * Procesamiento (raw -> clean)
  * Entrenamiento de 3 modelos (Gradient Boosting)
  * Selección del mejor por MAE
  * Registro en MLflow y actualización del tag `best_model`
  * Generación de explicación SHAP

![image](https://github.com/user-attachments/assets/bf90bdb6-82fd-497f-85f4-ea48165c2b3e)

### 2. `api/`

* `main.py`: FastAPI para realizar inferencias con el modelo etiquetado como `best_model` en MLflow
* Expone:

  * `/predict`: endpoint de inferencia
  * `/metrics`: endpoint de métricas con Prometheus para monitoreo

![image](https://github.com/user-attachments/assets/f2401f9e-578b-41dc-9022-04aa1f894e19)

### 3. `ui/`

* `app.py`: Interfaz Gradio para ingresar datos y visualizar predicción
* Incluye:

  * Nombre del modelo
  * Visual SHAP
  * Historial de modelos entrenados y métricas de cada uno
 
![image](https://github.com/user-attachments/assets/0d854bd3-c3b0-417b-977d-fe09d5d64738)

### 4. `analysis/`

* Scripts iniciales para la exploración de la API de ingesta de datos
* Incluye algunos archivos de las respuestas de la API en cada request

### 5. `Dockerfile.*`

* `Dockerfile` en cada servicio personalizado (Airflow, API, Gradio)
* `Dockerfile.mlflow`: imagen personalizada de MLflow

### 6. `k8s/`

* Manifiestos de todos los servicios:

  * `airflow/`: incluye scheduler, triggerer, worker, webserver, redis y postgres
  * `fastapi/`, `gradio/`, `mlflow/`.
  * `grafana/`, `prometheus/`, `minio/`, `mysql-data/`,`mysql-mlflow/`, `project-secrets.yaml`
* `application.yaml`: definición de ArgoCD para sincronización automática
* `kustomization.yaml`: gestión de recursos de ArgoCD

## CI/CD con GitHub Actions y Argo CD

* `/.github/workflows/deploy.yaml`

  * Se ejecuta en push a `main`
  * Crea y publica imagen Docker para cada servicio con imagen personalizada (`airflow`, `mlflow`, `fastapi`, `gradio`) con tag `:<sha>`
  * Actualiza manifiestos en `k8s/` con dicho tag
  * ArgoCD detecta cambios y redespliega servicios

### GitHub Actions 
![image](https://github.com/user-attachments/assets/88a4b188-129c-47bf-abaf-81bafa06341b)

### Argo CD
![image](https://github.com/user-attachments/assets/8d08696f-5651-4913-b8cb-4685e7c254a1)

## MLflow y Monitoreo

* Cada modelo se registra como `run` en MLflow:

  * MAPE, RMSE, SHAP.
  * `tags.stage = best_model` para inferencia
 
![image](https://github.com/user-attachments/assets/b8aa9b05-a4aa-4389-b065-d9b3a82f108c)
    
* Prometheus registra y Grafana muestra:

  * Total de predicciones
  * Latencia de inferencia
  * Tamaño del batch de inferencia
  * Errores en predicción

### Prometheus 
![image](https://github.com/user-attachments/assets/2096a842-8eee-48b2-9860-c1ded8c9aafc)

### Grafana
![image](https://github.com/user-attachments/assets/26da0ed3-5074-42a8-a770-c66467f0ba8e)

## Secretos y configuración

* `project-secrets.yaml`: incluye

  * Credenciales de MinIO
  * Rutas a servicios (`MLFLOW_TRACKING_URI`, `FASTAPI_PREDICT_URL`)
  * Variables de conexión a PostgreSQL y MySQL

## Restricciones y Validaciones

* Si no hay nuevos datos o no se cumplen criterios de entrenamiento:

  * El DAG termina exitosamente sin error
* Solo un modelo mantiene el tag `best_model`, los demás se archivan
* SHAP se genera y registra como artefacto en MLflow

## Requisitos Previos

* Docker
* Kubernetes (microk8s)
* Argo CD instalado (dashboard y CLI)
* Secrets cargados en el cluster

## Ejecución Manual (dev)

```bash
# Comandos para nodo master:
sudo snap install microk8s --classic
sudo microk8s enable dns storage ingress
sudo usermod -a -G microk8s $USER
newgrp microk8s
microk8s add-node - Obtener el comando para unir el node worker de la otra máquina virtual

# Comandos nodo worker:
sudo snap install microk8s --classic
sudo microk8s enable dns storage ingress
sudo usermod -a -G microk8s $USER
newgrp microk8s
microk8s join 10.43.101.165:25000/.... --worker

# Aplicar manifiestos 
kubectl apply -f project-secrets.yaml
kubectl apply -f nombre-del-manifiesto.yaml

# Comandos útiles:
kubectl get pods -o wide - revisar todos los pods levantados
kubectl get svc -o wide - revisar todos los servicios levantados
```

## Ubicación de cada servicio:

- Minio: http://10.43.101.165:30901
- MLFlow: http://10.43.101.165:30500
- Airflow: http://10.43.101.165:30080
- API inferencia: http://10.43.101.165:30800/docs
- Gradio: http://10.43.101.165:30850
- Prometheus: http://10.43.101.201:30910
- Grafana: http://10.43.101.201:30300
- ArgoCD: http://10.43.101.201:30407

## ArgoCD 

```bash
# Crear la aplicación si no existe
kubectl apply -f proyecto_4/k8s/application.yaml -n argocd

# Verificar estado
kubectl get applications -n argocd
kubectl describe application proyecto-4 -n argocd
```

## Estado Final Esperado

* ArgoCD sincronizado, todos los pods corriendo
* FastAPI y Gradio respondiendo en su NodePort
* MLflow accesible con histórico
* Grafana mostrando dashboards completos
* DAG ejecutándose cada 15 minutos

# Link al video de sustentación en Youtube: https://www.youtube.com/watch?v=sA6Kg9LZmzg 
