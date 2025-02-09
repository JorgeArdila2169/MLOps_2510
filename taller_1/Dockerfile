# Usar una imagen base de Python
FROM python:3.9

# Configurar el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivos necesarios
COPY main.py .
COPY models/ models/
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8989
EXPOSE 8989

# Comando para ejecutar la API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8989"]