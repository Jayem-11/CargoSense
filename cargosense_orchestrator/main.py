import requests
from fastapi import FastAPI, Request, HTTPException


app = FastAPI(title="CargoSense")

BASES = {
    "ingestion": "https://maestro-0bec3790-eb0d-45ca-919b-d3ba8e39987a-zcaxlbuauq-uc.a.run.app/ingest",
    "geocode": "https://maestro-b8c0d5ad-347d-44a4-8eb4-484de0b017ab-zcaxlbuauq-uc.a.run.app/geocode_enrich",
    "weather": "https://maestro-0367185f-c6c6-43bb-9315-12cc4b17d9a8-zcaxlbuauq-uc.a.run.app/enrich_weather",
    "traffic": "https://maestro-18d44df7-8b0d-44e2-8322-a74cfc7876cc-zcaxlbuauq-uc.a.run.app/enrich_congestion",
    "features": "https://maestro-bd5db7bb-ed52-42e7-81da-e069b695b160-zcaxlbuauq-uc.a.run.app/build_features",
    # "risk": "https://maestro-6335e4e6-a469-45e7-9764-e5f7928b88e2-zcaxlbuauq-uc.a.run.app/score",
    "risk": "https://maestro-14b52318-f86b-4ff1-9a83-82edfc4215cf-zcaxlbuauq-uc.a.run.app/score",
    "explain": "https://maestro-05e7beeb-2a1a-49d9-bfe2-5eb7799c91aa-zcaxlbuauq-uc.a.run.app/explain",
    "notify": "https://maestro-8881cf6e-c07b-4bce-98a3-34318e42cdfd-zcaxlbuauq-uc.a.run.app/notify",
}

def call(agent, payload):
    resp = requests.post(BASES[agent], json=payload)
    return resp.json()


# Required shipment fields
REQUIRED_FIELDS = [
    "shipment_id",
    "origin",
    "destination",
    "carrier",
    "dispatch_ts",
    "expected_ts"
]

def validate_shipments(shipments: list):
    """Check all shipments for missing fields before processing."""
    for i, shipment in enumerate(shipments, start=1):
        missing = [f for f in REQUIRED_FIELDS if f not in shipment or shipment[f] in ("", None)]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Shipment {i} missing field(s): {', '.join(missing)}"
            )

def run_pipeline(data):
    shipment_records = []
    processed_records = []

    for entry in data:
        record = call("ingestion",entry)
        shipment_records.append(record["processed"])

    for ship in shipment_records:
        s = call("geocode", ship)
        w = call("weather", s)
        t = call("traffic", w)
        fts = call("features", t)
        r = call("risk", fts)
        e = call("explain", r)
        n = call("notify", e)
        processed_records.append(n)
    return processed_records


@app.get("/health")
def health():
    return {"status": "CargoSense alive"}

@app.post("/cargosense")
async def notify_endpoint(request: Request):
    shipment = await request.json()
    # Ensure it's a list
    if not isinstance(shipment, list):
        raise HTTPException(status_code=400, detail="Input must be a list of shipments")

    # validate before running pipeline
    validate_shipments(shipment)

    output = run_pipeline(shipment)
    return {"processed_shipments": output}