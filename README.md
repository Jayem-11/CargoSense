# 🚚 CargoSense 
   
**smarter routes, seamless delivery**

#### 📌 Inspiration

Delays in cargo shipments cost businesses time, money, and trust. We wanted to explore how agents can help predict risks (traffic, weather, carrier reliability) and provide actionable insights in real-time.

---

## 🛠️ Architecture

```
flowchart LR
    Ingestion[Ingestion Agent] --> Geocode[Geocode & Route Agent]
    Geocode --> Weather[Weather Agent]
    Weather --> Traffic[Traffic Agent]
    Traffic --> FeatureBuilder[Feature Builder]
    FeatureBuilder --> RiskModel[Risk Model]
    RiskModel --> Explanation[Explanation Agent]
    Explanation --> Notify[Notify Agent]
```

* **Ingestion Agent** – validates & standardizes shipment input.
* **Geocode & Route Agent** – fetches route distance/travel time (TomTom API).
* **Weather Agent** – pulls weather conditions.
* **Traffic Agent** – gets congestion information.
* **Feature Builder** – combines features into a risk profile.
* **Risk Model** – predicts delay probability & risk level using a `RandomForestClassifier` and a baseline risk score.
* **Explanation Agent** – generates human-readable summaries using `gemini-2.5-flash`.
* **Notify Agent** – Give alerts.

---

## 🚀 Setup

1. **Clone the repo**

```bash
git clone https://github.com/yourusername/cargosense.git
cd cargosense
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Environment variables**
   Create `.env`:

```bash
TOMTOM_KEY=your_tomtom_api_key
OPEN_METEO_URL="enter url"
```

4. **Run locally** (via FastAPI)
   Each agent is containerized. Example for orchestrator:

```bash
uvicorn cargosense_orchestrator.main:app --reload
```

---

## 🌐 Example API Calls

Endpoint: `https://maestro-3a737890-231b-45e5-a197-ce006ba9bd02-zcaxlbuauq-uc.a.run.app/cargosense`

### Cargosense Input

```json
[
  {
    "shipment_id": "SHP-1001",
    "origin": "Nairobi",
    "destination": "Mombasa",
    "carrier": "DHL",
    "dispatch_ts": "2025-08-27T08:00:00Z",
    "expected_ts": "2025-08-28T18:00:00Z"
  },
  {
    "shipment_id": "SHP-1002",
    "origin": "Kisumu",
    "destination": "Eldoret",
    "carrier": "FedEx",
    "dispatch_ts": "2025-08-27T09:30:00Z",
    "expected_ts": "2025-08-27T20:00:00Z"
  }
]

```

Carriers: Only these carriers are supported for now `DHL` `UPS` `FedEx` `Posta`

✅ Response:

```json
{
    "processed_shipments": [
        {
            "shipment_id": "SHP-1001",
            "origin": "NAIROBI",
            "destination": "MOMBASA",
            "carrier": "DHL",
            "dispatch_ts": "2025-08-27T08:00:00Z",
            "expected_ts": "2025-08-28T18:00:00Z",
            "geocode_ok": true,
            "origin_lat": -1.2857857,
            "origin_lon": 36.8200253,
            "dest_lat": -4.0574645,
            "dest_lon": 39.663945,
            "distance_km": 487.63,
            "duration_hr": 8.58,
            "route_points": [
                [
                    -1.28604,
                    36.82016
                ],
                [
                    -1.28566,
                    36.82087
                ],
                [
                    -1.2856,
                    36.82098
                ],
                [
                    -1.28595,
                    36.82116
                ],
                [
                    -1.28609,
                    36.82122
                ],
                [
                    -1.28614,
                    36.82111
                ],
                [
                    -1.28635,
                    36.82071
                ],
                [
                    -1.28647,
                    36.82048
                ],
                [
                    -1.28651,
                    36.82041
                ],
                [
                    -1.28665,
                    36.82012
                ]
            ],
            "route_max_rain_mm": 1.6,
            "route_max_wind_kph": 14.7,
            "route_storm": 0,
            "congestion_index": 0.53,
            "features": {
                "shipment_id": "SHP-1001",
                "distance_km": 487.63,
                "hours_to_deadline": 34.0,
                "origin_rain_mm": 0.0,
                "origin_storm": 0,
                "congestion_index": 0.53,
                "carrier_reliability": 0.83
            },
            "baseline_delay_prob": 0.329,
            "ml_delay_prob": 0.04,
            "delay_prob": 0.329,
            "risk_level": "MEDIUM",
            "source": "baseline",
            "summary": "Shipment SHP-1001 has a medium risk of delay (32.9% probability) primarily due to moderate congestion along the significant route from Nairobi to Mombasa.",
            "actions": [
                "Monitor real-time traffic conditions on the Nairobi-Mombasa route.",
                "Proactively inform the customer about the medium delay risk and potential impact.",
                "Verify carrier's contingency plans for managing congestion-related delays."
            ],
            "explained_by": "gemini",
            "notification": "Shipment SHP-1001 is at MEDIUM risk of delay. Monitor closely."
        },
        {
            "shipment_id": "SHP-1002",
            "origin": "KISUMU",
            "destination": "ELDORET",
            "carrier": "FedEx",
            "dispatch_ts": "2025-08-27T09:30:00Z",
            "expected_ts": "2025-08-27T20:00:00Z",
            "geocode_ok": true,
            "origin_lat": -0.1030863,
            "origin_lon": 34.7560645,
            "dest_lat": 0.5184695,
            "dest_lon": 35.2739056,
            "distance_km": 123.75,
            "duration_hr": 2.76,
            "route_points": [
                [
                    -0.10311,
                    34.75604
                ],
                [
                    -0.10316,
                    34.75608
                ],
                [
                    -0.10318,
                    34.75608
                ],
                [
                    -0.1032,
                    34.75608
                ],
                [
                    -0.10321,
                    34.75606
                ],
                [
                    -0.10333,
                    34.75591
                ],
                [
                    -0.10332,
                    34.75588
                ],
                [
                    -0.10328,
                    34.75583
                ],
                [
                    -0.10326,
                    34.75572
                ],
                [
                    -0.10321,
                    34.75577
                ]
            ],
            "route_max_rain_mm": 0.4,
            "route_max_wind_kph": 13.3,
            "route_storm": 0,
            "congestion_index": 0.0,
            "features": {
                "shipment_id": "SHP-1002",
                "distance_km": 123.75,
                "hours_to_deadline": 10.5,
                "origin_rain_mm": 0.0,
                "origin_storm": 0,
                "congestion_index": 0.0,
                "carrier_reliability": 0.73
            },
            "baseline_delay_prob": 0.244,
            "ml_delay_prob": 0.04,
            "delay_prob": 0.244,
            "risk_level": "LOW",
            "source": "baseline",
            "summary": "Shipment SHP-1002 has a low probability of delay, with current conditions indicating no significant weather or congestion risks.",
            "actions": [
                "Monitor shipment progress for any unforeseen changes.",
                "Maintain communication with carrier FedEx to ensure timely delivery.",
                "No immediate intervention required due to the low-risk assessment."
            ],
            "explained_by": "gemini",
            "notification": "Shipment SHP-1002 is at LOW risk of delay. No action needed."
        }
    ]
}
```

---

## ⚖️ Tradeoffs

* **Data sources**: We used free-tier APIs (TomTom, OpenWeather). Limited quota may affect scale.
* **Gemini**: We used the free version of `gemini-2.5-flash`. This comes with Limits.
* **RandomForestClassifier**: This model was trained using synthetic data. Realtime data collected should be used in future.
* **Carrier reliability**: Static values were used instead of real-time reliability feeds due to lack of free APIs.
---

## 🔮 Future Work

* Integrate **real-time carrier performance APIs**.
* Add **dashboards** for visual monitoring of shipments.
* Train a **custom ML model** using historical shipping datasets to forcast the risk probability.

