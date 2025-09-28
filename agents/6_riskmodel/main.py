from fastapi import FastAPI, Request
import pickle
import numpy as np
import os

app = FastAPI(title="Shipment Risk Scoring Agent")

# Try loading ML model
MODEL_PATH = "shipment_delay_model.pkl"
model = None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

# -------- Baseline rule-based model --------
def baseline_score(features: dict) -> float:
    p = 0.15
    p += min(features.get("distance_km", 0) / 1000.0, 0.15)
    p += 0.25 if features.get("origin_storm", 0) else 0.0
    p += min(features.get("origin_rain_mm", 0.0) / 50.0, 0.15)
    p += min(features.get("congestion_index", 0.2) * 0.3, 0.30)
    p -= max(0.0, (features.get("carrier_reliability", 0.7) - 0.7))  # better carrier reduces risk
    return max(0.0, min(p, 0.99))

# -------- ML model predictor --------
def ml_score(features: dict) -> float | None:
    if model is None:
        return None  # fallback if model isn't loaded

    numeric_features = {
        "distance_km": features.get("distance_km", 0.0),
        "hours_to_deadline": features.get("hours_to_deadline", 0.0),
        "origin_rain_mm": features.get("origin_rain_mm", 0.0),
        "origin_storm": features.get("origin_storm", 0),
        "congestion_index": features.get("congestion_index", 0.0),
        "carrier_reliability": features.get("carrier_reliability", 0.7),
    }

    arr = np.array([[numeric_features["distance_km"],
                 numeric_features["hours_to_deadline"],
                 numeric_features["origin_rain_mm"],
                 numeric_features["origin_storm"],
                 numeric_features["congestion_index"],
                 numeric_features["carrier_reliability"]]])

    prob = model.predict_proba(arr)[0][1]
    return float(prob)

# -------- Unified risk function --------
def add_risk(shipment: dict) -> dict:
    f = shipment.get("features", {})

    # Compute both
    base_prob = baseline_score(f)
    ml_prob = ml_score(f) if model else None

    # Choose the larger one
    if ml_prob is not None:
        delay_prob = max(base_prob, ml_prob)
        source = "ML" if ml_prob >= base_prob else "baseline"
    else:
        delay_prob = base_prob
        source = "baseline"

    # Store everything
    shipment["baseline_delay_prob"] = round(base_prob, 3)
    shipment["ml_delay_prob"] = round(ml_prob, 3) if ml_prob is not None else None
    shipment["delay_prob"] = round(delay_prob, 3)
    shipment["risk_level"] = (
        "HIGH" if delay_prob >= 0.6 else "MEDIUM" if delay_prob >= 0.3 else "LOW"
    )
    shipment["source"] = source
    return shipment

@app.get("/health")
def health():
    return {"status": "alive"}

@app.post("/score")
async def score_endpoint(request: Request):
    shipment = await request.json()
    return add_risk(shipment)
