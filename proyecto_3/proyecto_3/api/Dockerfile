# Imagen base de Python
FROM python:3.7

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir fastapi uvicorn pandas numpy scikit-learn==1.0.2 mlflow python-dotenv boto3 pydantic==1.10.12 prometheus_client dill==0.3.1.1 cloudpickle==2.2.1 psutil==5.9.5

# Exponer el puerto de la API
EXPOSE 8000

# Comando para iniciar la API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
