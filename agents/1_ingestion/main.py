from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Ingestion Agent")

# Define input schema
class Shipment(BaseModel):
    shipment_id: str
    origin: str
    destination: str
    carrier: str
    dispatch_ts: str
    expected_ts: str

@app.get("/health")
def health():
    return {"status": "alive"}

@app.post("/ingest")
def ingest(shipment: Shipment):
    processed = {
        "shipment_id": shipment.shipment_id,
        "origin": shipment.origin.upper(),
        "destination": shipment.destination.upper(),
        "carrier": shipment.carrier,
        "dispatch_ts": shipment.dispatch_ts,
        "expected_ts": shipment.expected_ts,
    }
    return {"processed": processed}
