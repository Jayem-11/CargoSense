from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Shipment Enrichment Agent")
API_KEY = os.getenv("TOMTOM")

# ---------------------------
# Pydantic models
# ---------------------------
class Shipment(BaseModel):
    shipment_id: str
    origin: str
    destination: str
    carrier: str | None = None
    dispatch_ts: str | None = None
    expected_ts: str | None = None

# ---------------------------
# Helper functions
# ---------------------------
def get_coords_tomtom(city_name: str):
    url = f"https://api.tomtom.com/search/2/geocode/{city_name}.json"
    params = {"key": API_KEY, "limit": 1}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"TomTom geocode error: {resp.text}")

    data = resp.json()
    if not data.get("results"):
        raise HTTPException(status_code=404, detail=f"No coordinates found for {city_name}")

    pos = data["results"][0]["position"]
    return {"lon": pos["lon"], "lat": pos["lat"]}


def get_route_tomtom(origin: dict, dest: dict):
    url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/"
        f"{origin['lat']},{origin['lon']}:{dest['lat']},{dest['lon']}/json"
    )
    params = {
        "key": API_KEY,
        "instructionsType": "text",
        "routeRepresentation": "polyline",
        "computeTravelTimeFor": "all",
    }

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"TomTom route error: {resp.text}")

    data = resp.json()
    summary = data["routes"][0]["summary"]
    distance = summary["lengthInMeters"]
    duration = summary["travelTimeInSeconds"]

    points = data["routes"][0]["legs"][0]["points"]
    coords = [(pt["latitude"], pt["longitude"]) for pt in points]

    return coords, distance, duration


def enrich(shipment: Shipment) -> dict:
    o, d = shipment.origin, shipment.destination
    try:
        ocoord = get_coords_tomtom(o)
        dcoord = get_coords_tomtom(d)
    except Exception as e:
        return {**shipment.dict(), "geocode_ok": False, "error": str(e)}

    route, distance, duration = get_route_tomtom(ocoord, dcoord)

    enriched = shipment.dict()
    enriched.update(
        {
            "geocode_ok": True,
            "origin_lat": ocoord["lat"],
            "origin_lon": ocoord["lon"],
            "dest_lat": dcoord["lat"],
            "dest_lon": dcoord["lon"],
            "distance_km": round(distance / 1000, 2),
            "duration_hr": round(duration / 3600, 2),
            "route_points": route[:10],  # sample first 10
        }
    )
    return enriched

# ---------------------------
# API Endpoints
# ---------------------------
@app.get("/health")
def health():
    return {"status": "alive"}

@app.post("/geocode_enrich")
def enrich_endpoint(shipment: Shipment):
    return enrich(shipment)

