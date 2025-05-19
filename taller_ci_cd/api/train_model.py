# Niveles/4/train_model.py
import pickle
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

def train_and_save_model():
    iris = load_iris()
    X, y = iris.data, iris.target
    model = RandomForestClassifier()
    model.fit(X, y)

    with open('app/model.pkl', 'wb') as f:
        pickle.dump(model, f)

if __name__ == "__main__":
    train_and_save_model()