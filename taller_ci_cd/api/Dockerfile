FROM python:3.9

WORKDIR /app
COPY ./app /app/app
COPY app/model.pkl /app/app/model.pkl
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]