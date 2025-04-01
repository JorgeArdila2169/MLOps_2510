# Usar una versión más reciente de Python
FROM python:3.10-slim

# Instalar y actualizar pip
RUN pip install --upgrade pip

# Crear y establecer directorio de trabajo
WORKDIR /app

# Copiar el archivo requirements.txt
COPY requirements.txt ./

# Instalar las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Asegurar que el entorno de UV se activa y esté en PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copiar el resto del código fuente
COPY . .

# Exponer los puertos necesarios
EXPOSE 80 8503

# Comando por defecto (puede ser overrideado en docker-compose)
CMD ["python", "main.py"]

