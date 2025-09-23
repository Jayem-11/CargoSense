# CargoSense 🚚
### smarter routes, seamless delivery

---

## 📌 Inspiration

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
* **Risk Model** – predicts delay probability & risk level.
* **Explanation Agent** – generates human-readable summaries.
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
   Each agent is containerized. Example for ingestion:

```bash
uvicorn agents.ingest:app --host 0.0.0.0 --port 8081
```

---

## 🌐 Example API Calls

### Ingestion Agent

```bash
curl -X POST http://localhost:8081/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SHP-1001",
    "origin": "Nairobi",
    "destination": "Mombasa",
    "carrier": "DHL",
    "dispatch_ts": "2025-08-27T08:00:00Z",
    "expected_ts": "2025-08-28T18:00:00Z"
  }'
```

✅ Response:

```json
{
  "processed": {
    "shipment_id": "SHP-1001",
    "origin": "NAIROBI",
    "destination": "MOMBASA",
    "carrier": "DHL",
    "dispatch_ts": "2025-08-27T08:00:00Z",
    "expected_ts": "2025-08-28T18:00:00Z"
  }
}
```

---

## ⚖️ Tradeoffs

* **Data sources**: We used free-tier APIs (TomTom, OpenWeather). Limited quota may affect scale.
* **Carrier reliability**: Static values were used instead of real-time reliability feeds due to lack of free APIs.
* **Orchestration**: Agents run independently via FastAPI; Maestro SDK could manage orchestration more robustly.
* **Database**: SQLite for simplicity → good for hackathons but not production-scale.

---

## 🔮 Future Work

* Integrate **real-time carrier performance APIs**.
* Use **streaming event pipelines** (Kafka, RabbitMQ) instead of HTTP chaining.
* Deploy on **Kubernetes** for scaling agents independently.
* Add **dashboards** for visual monitoring of shipments.
* Train a **custom ML model** using historical shipping datasets.

---

## ✅ Example Workflow

1. Call `/ingest` with shipment details.
2. It triggers geocode → weather/traffic → features → risk → explanation.
3. Final JSON:

```json
{
  "shipment_id": "SHP-1001",
  "delay_prob": 0.67,
  "risk_level": "HIGH",
  "summary": "High risk of delay due to heavy traffic and moderate weather disruptions."
}
```

---

