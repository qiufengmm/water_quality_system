"""Generate sample water quality dataset for testing and demo."""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# Station configuration
STATIONS = {
    "ST001": {"name": "水源地A", "base_ph": 7.2, "base_do": 7.0, "base_nh3n": 0.12},
    "ST002": {"name": "河流断面B", "base_ph": 7.5, "base_do": 6.0, "base_nh3n": 0.25},
    "ST003": {"name": "排污口C", "base_ph": 7.8, "base_do": 4.5, "base_nh3n": 0.45},
}

# Normal ranges
RANGES = {
    "ph": (6.5, 8.5),
    "do": (5.0, 9.0),
    "nh3n": (0.01, 0.8),
    "turbidity": (0.5, 15.0),
    "temperature": (8.0, 32.0),
    "cod": (5.0, 35.0),
    "total_phosphorus": (0.01, 0.4),
}


def generate_weekly_data(start_date: datetime, days: int = 30, interval_hours: int = 4) -> pd.DataFrame:
    """Generate a realistic water quality dataset spanning multiple days."""
    records = []
    total_points = days * 24 // interval_hours

    for i in range(total_points):
        timestamp = start_date + timedelta(hours=i * interval_hours)

        for station_id, station_info in STATIONS.items():
            record = {
                "station_id": station_id,
                "collection_time": timestamp,
            }

            hour = timestamp.hour
            for indicator, (min_val, max_val) in RANGES.items():
                # Base value with station-specific adjustments
                if indicator == "ph":
                    base = station_info["base_ph"]
                elif indicator == "do":
                    base = station_info["base_do"]
                elif indicator == "nh3n":
                    base = station_info["base_nh3n"]
                else:
                    base = (min_val + max_val) / 2

                # Add diurnal variation and noise
                diurnal = 0
                if indicator == "temperature":
                    diurnal = 3 * np.sin(2 * np.pi * (hour - 6) / 24)
                elif indicator == "do":
                    diurnal = 0.5 * np.sin(2 * np.pi * (hour - 14) / 24)
                elif indicator == "ph":
                    diurnal = 0.2 * np.sin(2 * np.pi * (hour - 10) / 24)

                noise = np.random.normal(0, (max_val - min_val) * 0.05)
                value = base + diurnal + noise

                # Clamp to reasonable range
                value = max(min_val * 0.5, min(value, max_val * 1.5))
                record[indicator] = round(float(value), 2)

            # Randomly introduce some missing values (2% probability)
            if random.random() < 0.02:
                col_to_null = random.choice(list(RANGES.keys()))
                record[col_to_null] = None

            # Randomly introduce some outliers (1% probability)
            if random.random() < 0.01:
                col_to_spike = random.choice(list(RANGES.keys()))
                if col_to_spike == "ph":
                    record[col_to_spike] = round(random.uniform(3.0, 11.0), 2)
                else:
                    record[col_to_spike] = round(
                        record[col_to_spike] * random.uniform(2.0, 5.0), 2
                    )

            records.append(record)

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    start = datetime(2026, 4, 1, 0, 0, 0)
    df = generate_weekly_data(start, days=30, interval_hours=4)

    output_path = "water_quality_sample.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Generated {len(df)} records across {len(STATIONS)} stations")
    print(f"Date range: {df['collection_time'].min()} to {df['collection_time'].max()}")
    print(f"Columns: {list(df.columns)}")
    print(f"Saved to: {output_path}")

    # Print sample
    print("\nSample records:")
    print(df.head(3).to_string())
