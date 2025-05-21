# Taller CI/CD - Despliegue de API de IA con FastAPI, Kubernetes y Argo CD
# Grupo 5

Este proyecto implementa una arquitectura de MLOps para entrenar, construir, desplegar y monitorear una API de predicción basada en un modelo de Machine Learning, utilizando:

- FastAPI para la API
- Kubernetes para orquestación de contenedores
- Docker para empaquetar la aplicación
- GitHub Actions para CI/CD
- Argo CD para GitOps y despliegue automático
- Prometheus y Grafana para observabilidad y monitoreo

## Estructura del proyecto:

![image](https://github.com/user-attachments/assets/a1109072-f85b-4cb8-8696-ecf80e794d55)

## Requisitos Previos

```markdown
- Tener instalado y configurado Docker
- Tener instalado MicroK8s con extensiones habilitadas: dns, storage, ingress, prometheus
- Tener una cuenta en Docker Hub y configurar secrets en GitHub
- Tener instalado kubectl y acceso al cluster MicroK8s
- Acceso a la interfaz web de Argo CD y Grafana

```
## Pasos para desplegar localmente:

1. Entrenar el modelo

```bash
cd taller_ci_cd/api
python train_model.py
```

2. Construir y subir imagenes a Dockerhub
```bash
docker build -t <usuario_docker>/api:latest .
docker push <usuario_docker>/api:latest

cd ../loadtester
docker build -t <usuario_docker>/loadtester:latest .
docker push <usuario_docker>/loadtester:latest
```

3. Aplicar manifiestos
```bash
kubectl apply -k taller_ci_cd/manifests
```

4. Configurar port-forward para los servicios de Argo CD y la API.
   Los servicios de Grafana y Prometheus están configurados con NodePort desde los manifiestos
```bash
kubectl port-forward service/api-service 8000:8000
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

## CI/CD con GitHub Actions

```markdown
El pipeline de GitHub Actions ejecuta automáticamente en cada push a `main`:

- Entrena el modelo
- Construye las imágenes Docker de API y LoadTester
- Publica las imágenes en Docker Hub
- Actualiza manifiestos y despliega

Secrets configurados en GitHub:

- `DOCKERHUB_USERNAME`: Usuario Docker Hub
- `DOCKERHUB_TOKEN`: Token o contraseña Docker Hub
- `PAT_TOKEN`: Token de acceso para el bot de Github Actions
```

Argo CD sincroniza automáticamente el estado del cluster con los manifiestos en el repositorio.
![image](https://github.com/user-attachments/assets/5c1ce12c-e2a9-42ed-b786-0d8f92492bd4)

Para configurar:

- Instalar Argo CD en MicroK8s
- Exponer la interfaz web de Argo CD
- Crear y aplicar el manifiesto `app.yaml` apuntando al repo y path `taller_ci_cd/manifests`
- Usar la UI para monitorear sincronización, estado y logs

Se implementa monitoreo con:

- Prometheus para recolectar métricas de la API
- Grafana para visualización de métricas en dashboards personalizados
![image](https://github.com/user-attachments/assets/a895eb0e-c0e5-40dc-979f-4e1d4c296455)

Accesos:

- Grafana: http://<ip_nodo>:32000
- Prometheus: http://<ip_nodo>:30900

Para el control de versiones de los manifiestos se utiliza el sha del commit correspondiente a la actualización en las imágenes de Docker
![image](https://github.com/user-attachments/assets/698e6d5c-29c3-49bd-8603-82cd7f74eb77)

La ejecución del workflow de Github Actions depende de un token de acceso personal (PAT_TOKEN) sobre el repositorio para que el bot logre realizar los push necesarios para actualizar los manifiestos con las imagenes nuevas, este token debe ser creado desde Github y agregado a los secretos del repositorio

## Comandos útiles
### Ver pods
```bash
kubectl get pods
```

### Ver servicios
```bash
kubectl get svc
```

### Aplicar manifests con kustomize
```bash
kubectl apply -k taller_ci_cd/manifests
```

### Ver logs
```bash
kubectl logs deployment/api-deployment
```

## Evidencia de servicios y pods en kubernetes
![image](https://github.com/user-attachments/assets/9dd797f9-0212-4546-ab19-d7cc2f6d13c2)
