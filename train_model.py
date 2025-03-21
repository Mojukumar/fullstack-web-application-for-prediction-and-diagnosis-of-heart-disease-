import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier


data = pd.read_csv("Heart_Disease_Prediction.csv")


feature_columns = ['Age', 'Chest pain type', 'BP', 'Cholesterol', 'Max HR', 'ST depression', 'Number of vessels fluro', 'Thallium']
target_column = 'Heart Disease'

X = data[feature_columns]
y = data[target_column]

model = RandomForestClassifier()
model.fit(X, y)


with open("heartdiseaseprediction.model", "wb") as f:
    pickle.dump(model, f)
