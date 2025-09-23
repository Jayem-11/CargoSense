import random
from datetime import datetime
from fastapi import FastAPI, Request

app = FastAPI(title="Feature Builder Agent")

def hours_between(a_iso, b_iso):
    try:
        a = datetime.fromisoformat(a_iso.replace("Z", "+00:00"))
        b = datetime.fromisoformat(b_iso.replace("Z", "+00:00"))
        return abs((b - a).total_seconds()) / 3600.0
    except Exception:
        return 24.0

# __define-ocg__: carrier reliability lookup with default + variation
def get_carrier_reliability(carrier: str) -> float:
    base_reliability = {
        "DHL": 0.82,
        "UPS": 0.78,
        "FedEx": 0.75,
        "Posta": 0.65,
    }
    default_reliability = 0.70
    reliability = base_reliability.get(carrier, default_reliability)
    
    # Add slight random variation to simulate live fluctuations
    variation = random.uniform(-0.03, 0.03)
    varOcg = max(0.0, min(1.0, reliability + variation))  # clamp [0,1]
    
    return round(varOcg, 2)

def build_features(s: dict) -> dict:
    hours_to_deadline = hours_between(s.get("dispatch_ts", ""), s.get("expected_ts", ""))
    features = {
        "shipment_id": s["shipment_id"],
        "distance_km": float(s.get("distance_km", 0)),
        "hours_to_deadline": float(round(hours_to_deadline, 2)),
        "origin_rain_mm": float(s.get("origin_rain_mm", 0.0)),
        "origin_storm": int(s.get("origin_storm", 0)),
        "congestion_index": float(s.get("congestion_index", 0.2)),
        "carrier_reliability": get_carrier_reliability(s.get("carrier", ""))
    }
    s["features"] = features
    return s

@app.get("/health")
def health():
    return {"status": "alive"}

@app.post("/build_features")
async def build_features_endpoint(request: Request):
    shipment = await request.json()
    return build_features(shipment)
