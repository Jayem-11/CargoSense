from fastapi import FastAPI, Request
import requests, os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
TOMTOM_KEY = os.getenv("TOMTOM")

def get_traffic_flow(lat, lon):
    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    params = {"point": f"{lat},{lon}", "key": TOMTOM_KEY}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        data = resp.json()["flowSegmentData"]
        current = data["currentSpeed"]
        free = data["freeFlowSpeed"]
        if free > 0:
            return 1.0 - (current / free)
    return None


def enrich_congestion(shipment, n_samples=3):
    points = shipment.get("route_points", [])
    if not points:
        return shipment
    
    step = max(1, len(points) // n_samples)
    subsampled = points[::step][:n_samples]

    scores = []
    for lat, lon in subsampled:
        score = get_traffic_flow(lat, lon)
        if score is not None:
            scores.append(score)
    if scores:
        shipment["congestion_index"] = round(sum(scores) / len(scores), 2)
    else:
        shipment["congestion_index"] = 0.3
    return shipment

# ---------------------------
# API Endpoints
# ---------------------------
@app.get("/health")
def health():
    return {"status": "alive"}
    
@app.post("/enrich_congestion")
async def enrich_endpoint(request: Request):
    shipment = await request.json()
    return enrich_congestion(shipment)
