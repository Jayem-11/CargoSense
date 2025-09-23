from fastapi import FastAPI, Request

app = FastAPI(title="Baseline Risk Scoring Agent")

def score(features: dict) -> float:
    p = 0.15
    p += min(features.get("distance_km", 0) / 1000.0, 0.15)
    p += 0.25 if features.get("origin_storm", 0) else 0.0
    p += min(features.get("origin_rain_mm", 0.0) / 50.0, 0.15)
    p += min(features.get("congestion_index", 0.2) * 0.3, 0.30)
    p -= max(0.0, (features.get("carrier_reliability", 0.7) - 0.7))  # better carrier reduces risk
    return max(0.0, min(p, 0.99))

def add_risk(shipment: dict) -> dict:
    f = shipment.get("features", {})
    delay_prob = score(f)
    shipment["delay_prob"] = round(delay_prob, 3)
    shipment["risk_level"] = (
        "HIGH" if delay_prob >= 0.6 else "MEDIUM" if delay_prob >= 0.3 else "LOW"
    )
    return shipment

@app.get("/health")
def health():
    return {"status": "alive"}

@app.post("/score")
async def score_endpoint(request: Request):
    shipment = await request.json()
    return add_risk(shipment)
