import random
import pandas as pd

def generate_shipment_data(n=1000, seed=42):
    random.seed(seed)
    records = []

    for i in range(1, n + 1):
        shipment_id = f"SHP-{1000+i}"

        # Features
        distance_km = round(random.uniform(50, 2000), 2)
        hours_to_deadline = round(random.uniform(2, 72), 1)
        origin_rain_mm = round(random.uniform(0, 50), 1)
        origin_storm = random.choice([0, 1]) if origin_rain_mm > 20 else 0
        congestion_index = round(random.uniform(0, 1), 2)
        carrier_reliability = round(random.uniform(0.5, 0.99), 2)

        # Synthetic delay probability formula
        delay_prob = (
            0.3 * (distance_km / 2000) +
            0.2 * (1 - carrier_reliability) +
            0.2 * congestion_index +
            0.2 * (origin_rain_mm / 50) +
            0.1 * origin_storm
        )
        delay_prob = round(min(1, delay_prob), 3)  # clamp between 0 and 1

        records.append({
            "shipment_id": shipment_id,
            "distance_km": distance_km,
            "hours_to_deadline": hours_to_deadline,
            "origin_rain_mm": origin_rain_mm,
            "origin_storm": origin_storm,
            "congestion_index": congestion_index,
            "carrier_reliability": carrier_reliability,
            "delay_prob": delay_prob
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    df = generate_shipment_data(1000)
    df.to_csv("hackathon/cargo/model/synthetic_shipments.csv", index=False)
    print("Synthetic dataset saved as synthetic_shipments.csv")
