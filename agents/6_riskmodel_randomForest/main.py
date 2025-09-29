from fastapi import FastAPI, Request
import requests

app = FastAPI(title="Shipment Risk Scoring Agent")

# Load Hugging Face API details
HF_API_URL = "https://jayem-11-risk-analysis.hf.space/predict"

# -------- Baseline rule-based model --------
def baseline_score(features: dict) -> float:
    p = 0.15
    p += min(features.get("distance_km", 0) / 1000.0, 0.15)
    p += 0.25 if features.get("origin_storm", 0) else 0.0
    p += min(features.get("origin_rain_mm", 0.0) / 50.0, 0.15)
    p += min(features.get("congestion_index", 0.2) * 0.3, 0.30)
    p -= max(0.0, (features.get("carrier_reliability", 0.7) - 0.7))  # better carrier reduces risk
    return max(0.0, min(p, 0.99))

# -------- ML model predictor via Hugging Face --------
def ml_score(features: dict) -> float | None:

    try:
        response = requests.post(
            HF_API_URL,
            json={"inputs": features},
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()

        # Expected HF format: {"delay_prob": 0.04, "risk_level": "LOW"}
        if isinstance(result, dict) and "delay_prob" in result:
            return {
                "ml_delay_prob": float(result["delay_prob"]),
                "ml_risk_level": result.get("risk_level", "UNKNOWN"),
            }

    except Exception as e:
        print("HF request failed:", e)
        return None

    return None

# -------- Unified risk function --------
def add_risk(shipment: dict) -> dict:
    f = shipment.get("features", {})

    # Compute both
    base_prob = baseline_score(f)
    ml_prob = ml_score(f)["ml_delay_prob"]

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
