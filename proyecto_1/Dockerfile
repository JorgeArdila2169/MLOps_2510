# Dockerfile para JupyterLab
FROM python:3.10

# Instalar UV y actualizar pip
RUN pip install --upgrade pip && pip install uv

# Crear directorio de trabajo
WORKDIR /app

# Inicializar UV y agregar dependencias
RUN uv init && uv add jupyterlab pandas scikit-learn tfx[tensorflow]

# Asegurar que el entorno de UV se activa y Jupyter esté en PATH
ENV PATH="/app/.venv/bin:$PATH"

# Instalar pip dentro del entorno virtual de UV
RUN /app/.venv/bin/python -m ensurepip --default-pip
RUN /app/.venv/bin/python -m pip install --upgrade pip

# Exponer puerto para Jupyter
EXPOSE 8888

# Comando de inicio
CMD ["/app/.venv/bin/jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--allow-root"]