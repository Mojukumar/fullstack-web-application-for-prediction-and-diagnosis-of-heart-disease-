import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle


data = pd.read_csv("Heart_Disease_Prediction.csv")


print(data.isnull().sum())


features = data[["Age", "Chest pain type", "BP", "Cholesterol", "Max HR", "ST depression", "Number of vessels fluro", "Thallium"]]
target = data['Heart Disease']


x_train, x_test, y_train, y_test = train_test_split(features, target, random_state=3136)


model = RandomForestClassifier()
model.fit(x_train, y_train)


y_pred = model.predict(x_test)
print(classification_report(y_test, y_pred))


with open("heartdiseaseprediction.model", "wb") as f:
    pickle.dump(model, f)

print("Model saved successfully.")
