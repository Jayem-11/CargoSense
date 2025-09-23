# Console  notification
from fastapi import FastAPI, Request

app = FastAPI(title="Notification Agent")

def notify(s: dict) -> dict:
    level = s.get("risk_level", "LOW")
    shipment_id = s.get("shipment_id", "UNKNOWN")

    if level == "HIGH":
        message = f"Shipment {shipment_id} is at HIGH risk of delay. Immediate attention required."
    elif level == "MEDIUM":
        message = f"Shipment {shipment_id} is at MEDIUM risk of delay. Monitor closely."
    else:
        message = f"Shipment {shipment_id} is at LOW risk of delay. No action needed."

    s["notification"] = message
    return s

@app.get("/health")
def health():
    return {"status": "alive"}

@app.post("/notify")
async def notify_endpoint(request: Request):
    shipment = await request.json()
    return notify(shipment)
