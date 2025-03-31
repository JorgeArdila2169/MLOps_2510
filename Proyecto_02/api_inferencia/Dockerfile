# Dockerfile (base para FastAPI y Streamlit)
FROM python:3.9-slim

# Crear y establecer directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt ./

# Instalar dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
COPY . .

# Comando por defecto (puede ser overrideado en docker-compose)
CMD ["python", "main.py"]
