# mlflow/train_model.py

import pandas as pd
import os
import glob
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

RAW_DIR = "../data/raw"
PROCESSED_DIR = "../data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def train():
    all_files = glob.glob(os.path.join(RAW_DIR, "batch_*.csv"))
    if len(all_files) < 10:
        print("No hay suficientes batches para entrenamiento.")
        return

    df_list = [pd.read_csv(f) for f in all_files]
    df = pd.concat(df_list, ignore_index=True)
    df.dropna(inplace=True)

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("Proyecto2")

    with mlflow.start_run():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(clf, "model")

        print(f"Modelo entrenado con accuracy: {acc}")

if __name__ == "__main__":
    train()
