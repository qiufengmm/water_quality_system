"""Simulated sensor data collector for generating realistic water quality data."""

import random
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd

from .base import BaseCollector, CollectResult


class SensorCollector(BaseCollector):
    """Simulates IoT sensor data collection for water quality monitoring.

    Generates realistic water quality data with configurable parameters
    including normal ranges and seasonal variations.
    """

    # Normal ranges for each indicator (min, max)
    NORMAL_RANGES = {
        "ph": (6.5, 8.5),
        "do": (5.0, 9.0),
        "nh3n": (0.01, 0.5),
        "turbidity": (0.5, 8.0),
        "temperature": (5.0, 35.0),
        "cod": (5.0, 25.0),
        "total_phosphorus": (0.01, 0.3),
    }

    # Probability of generating an anomaly
    ANOMALY_PROBABILITY = 0.02

    def __init__(self):
        super().__init__("sensor_simulator")

    def collect(self,
                station_id: str = "ST001",
                start_time: Optional[datetime] = None,
                hours: int = 24,
                interval_minutes: int = 60,
                **kwargs) -> CollectResult:
        """Generate simulated sensor data.

        Args:
            station_id: Monitoring station identifier.
            start_time: Start time for data generation.
            hours: Number of hours of data to generate.
            interval_minutes: Data collection interval in minutes.

        Returns:
            CollectResult with generated data.
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=hours)

        timestamps = [
            start_time + timedelta(minutes=i * interval_minutes)
            for i in range(int(hours * 60 / interval_minutes))
        ]

        records = []
        for ts in timestamps:
            record = self._generate_record(station_id, ts)
            records.append(record)

        df = pd.DataFrame(records)
        self._data = df

        return CollectResult(
            success=True,
            records=df,
            record_count=len(df),
            message=f"Generated {len(df)} simulated sensor records for {station_id}"
        )

    def _generate_record(self, station_id: str, timestamp: datetime) -> dict:
        """Generate a single water quality data record with realistic values."""
        record = {
            "station_id": station_id,
            "collection_time": timestamp,
        }

        for indicator, (min_val, max_val) in self.NORMAL_RANGES.items():
            if random.random() < self.ANOMALY_PROBABILITY:
                # Generate anomaly (below min or above max)
                if random.random() < 0.5:
                    value = round(min_val - random.uniform(0.5, 2.0), 2)
                else:
                    value = round(max_val + random.uniform(0.5, 3.0), 2)
            else:
                # Generate normal value with slight seasonal variation
                base = (min_val + max_val) / 2
                amplitude = (max_val - min_val) / 2 * 0.8
                # Add time-of-day variation for temperature
                hour = timestamp.hour
                hour_factor = np.sin(2 * np.pi * (hour - 6) / 24) if indicator == "temperature" else 0
                value = round(
                    base + random.uniform(-amplitude, amplitude) + hour_factor * 2,
                    2
                )
                value = max(min_val * 0.5, min(value, max_val * 1.5))

            record[indicator] = value

        return record
