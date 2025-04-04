# Imagen base de Python
FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY main.py .

# Instalar dependencias
RUN pip install fastapi uvicorn numpy joblib xgboost dill pydantic

# Exponer el puerto de la API
EXPOSE 8000

# Comando para iniciar la API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
