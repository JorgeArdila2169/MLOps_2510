# Imagen base de Python
FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY main.py .

# Instalar dependencias
RUN pip install fastapi uvicorn numpy==1.24.4 mlflow dill pydantic boto3 scipy==1.11.4 scikit-learn==1.2.2 psutil==7.0.0 cloudpickle==2.2.1

# Exponer el puerto de la API
EXPOSE 7000

# Comando para iniciar la API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]
