from fastapi import FastAPI, Request
import pickle
import numpy as np
import os

app = FastAPI(title="Shipment Delay Prediction API")

# -------- Load ML model --------
MODEL_PATH = "shipment_delay_model.pkl"
model = None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)


# -------- ML predictor --------
def ml_score(features: dict) -> float:
    arr = np.array([[
        features.get("distance_km", 0.0),
        features.get("hours_to_deadline", 0.0),
        features.get("origin_rain_mm", 0.0),
        features.get("origin_storm", 0),
        features.get("congestion_index", 0.0),
        features.get("carrier_reliability", 0.7),
    ]])

    if hasattr(model, "predict_proba"):  # classifier
        return float(model.predict_proba(arr)[0][1])
    return float(model.predict(arr)[0])  # regression


# -------- API endpoints --------
@app.get("/health")
def health():
    return {"status": "alive", "model_loaded": model is not None}

@app.post("/predict")
async def predict_endpoint(request: Request):
    shipment = await request.json()
    features = shipment.get("features", {})

    if model is None:
        return {"error": "Model not loaded on server."}

    delay_prob = ml_score(features)
    return {
        "delay_prob": round(delay_prob, 3),
        "risk_level": "HIGH" if delay_prob >= 0.6 else "MEDIUM" if delay_prob >= 0.3 else "LOW"
    }
