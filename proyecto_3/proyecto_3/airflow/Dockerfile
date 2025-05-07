FROM apache/airflow:2.6.0

USER airflow

# Instalar paquetes adicionales
RUN pip install --no-cache-dir pandas numpy scikit-learn joblib mlflow requests matplotlib seaborn ipywidgets boto3 sqlalchemy pymysql

# Copiar DAGs al contenedor
COPY dags/ /opt/airflow/dags/
