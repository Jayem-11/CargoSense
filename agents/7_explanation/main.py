from fastapi import FastAPI, Request

app = FastAPI(title="Explanation Agent")

def explain(s: dict) -> dict:
    parts = []
    f = s["features"]

    if f.get("origin_storm"):
        parts.append("heavy storm at origin")
    if f.get("origin_rain_mm", 0) > 10:
        parts.append("significant rainfall")
    if f.get("congestion_index", 0) >= 0.5:
        parts.append("peak-hour congestion")
    if f.get("distance_km", 0) > 400:
        parts.append("long route distance")
    if not parts:
        parts.append("minor traffic and weather factors")

    actions = []
    if s.get("delay_prob", 0) >= 0.6:
        actions = ["Notify customer of possible delay", "Consider alternate route or dispatch offset"]
    elif s.get("delay_prob", 0) >= 0.3:
        actions = ["Monitor closely", "Pre-position resources for potential delay"]
    else:
        actions = ["No action needed"]

    s["summary"] = f"Order {s['shipment_id']} risk {int(s['delay_prob']*100)}% due to " + ", ".join(parts) + "."
    s["actions"] = actions
    return s

@app.get("/health")
def health():
    return {"status": "alive"}

@app.post("/explain")
async def explain_endpoint(request: Request):
    shipment = await request.json()
    return explain(shipment)
