FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos y luego instalar las dependencias
RUN pip install --upgrade pip && pip install requests gradio==4.15.0

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que Gradio se ejecutará
EXPOSE 8503

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
