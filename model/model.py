import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pickle

# Load dataset
df = pd.read_csv("hackathon/cargo/model/synthetic_shipments.csv")

# Create binary target
df["delayed"] = (df["delay_prob"] > 0.5).astype(int)

# Features & target
X = df.drop(columns=["shipment_id", "delay_prob", "delayed"])
y = df["delayed"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluation
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))


# Save model with pickle
with open("hackathon/cargo/model/shipment_delay_model.pkl", "wb") as f:
    pickle.dump(clf, f)

print("Model trained and saved as shipment_delay_model.pkl")