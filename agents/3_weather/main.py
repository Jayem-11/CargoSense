import requests
import numpy as np
from fastapi import FastAPI, Request
# from pydantic import BaseModel

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

app = FastAPI(title="Weather Enrichment Agent")


# ---------------------------
# Helper functions
# ---------------------------
def sample_route(lat1, lon1, lat2, lon2, n_points=5):
    """Generate n_points along straight line between origin and destination"""
    lats = np.linspace(lat1, lat2, n_points)
    lons = np.linspace(lon1, lon2, n_points)
    return list(zip(lats, lons))

def get_weather(lat, lon, timeout=5):
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation,wind_speed_10m",
            "forecast_days": 1,
        }
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # Take simple daily max for quick risk scoring
        rain = max(data["hourly"]["precipitation"])
        wind = max(data["hourly"]["wind_speed_10m"])
        return rain, wind
    except Exception:
        return 0.0, 0.0


def enrich_weather(shipment, n_samples=5) -> dict:
    # Use precomputed ORS route if available
    if shipment["route_points"]:
        step = max(1, len(shipment["route_points"]) // n_samples)
        points = shipment["route_points"][::step][:n_samples]
    else:
        points = sample_route(
            shipment.origin_lat, shipment.origin_lon,
            shipment.dest_lat, shipment.dest_lon,
            n_points=n_samples,
        )

    rains, winds = [], []
    for lat, lon in points:
        rain, wind = get_weather(lat, lon)
        rains.append(rain)
        winds.append(wind)

    max_rain, max_wind = max(rains), max(winds)
    storm = int(max_rain > 15 and max_wind > 35)

    enriched = shipment
    enriched.update({
        "route_max_rain_mm": max_rain,
        "route_max_wind_kph": max_wind,
        "route_storm": storm,
    })
    return enriched


# ---------------------------
# API Endpoints
# ---------------------------
@app.get("/health")
def health():
    return {"status": "alive"}


@app.post("/enrich_weather")
async def enrich_weather_endpoint(request: Request):
    shipment = await request.json()
    return enrich_weather(shipment)
