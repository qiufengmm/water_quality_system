"""Unit tests for data collection modules."""

import os
import tempfile
from datetime import datetime

import pandas as pd
import pytest

from src.data_collection import CsvCollector, ManualCollector, SensorCollector


class TestCsvCollector:
    """Tests for CSV/Excel data import."""

    def setup_method(self):
        self.collector = CsvCollector()

    def test_import_valid_csv(self):
        """Test importing a valid CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8-sig") as f:
            f.write("station_id,collection_time,ph,do,nh3n\n")
            f.write("ST001,2026-05-01 08:00:00,7.2,6.5,0.15\n")
            f.write("ST002,2026-05-01 09:00:00,7.5,5.8,0.22\n")
            tmp_path = f.name

        try:
            result = self.collector.collect(tmp_path)
            assert result.success
            assert result.record_count == 2
            assert result.errors == []
        finally:
            os.unlink(tmp_path)

    def test_import_with_chinese_columns(self):
        """Test importing CSV with Chinese column names."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8-sig") as f:
            f.write("站点,监测时间,pH,溶解氧,氨氮\n")
            f.write("ST001,2026-05-01 08:00:00,7.2,6.5,0.15\n")
            tmp_path = f.name

        try:
            result = self.collector.collect(tmp_path)
            assert result.success
            assert "station_id" in result.records.columns
            assert "collection_time" in result.records.columns
        finally:
            os.unlink(tmp_path)

    def test_file_not_found(self):
        """Test error handling for non-existent file."""
        result = self.collector.collect("nonexistent.csv")
        assert not result.success
        assert "not found" in result.message.lower()

    def test_unsupported_format(self):
        """Test error handling for unsupported file format."""
        result = self.collector.collect("data.txt")
        assert not result.success


class TestSensorCollector:
    """Tests for simulated sensor data generation."""

    def setup_method(self):
        self.collector = SensorCollector()

    def test_generate_data(self):
        """Test basic data generation."""
        result = self.collector.collect(
            station_id="ST001",
            hours=24,
            interval_minutes=60,
        )
        assert result.success
        assert result.record_count == 24
        assert "station_id" in result.records.columns
        assert "ph" in result.records.columns

    def test_custom_station(self):
        """Test data generation with custom station ID."""
        result = self.collector.collect(station_id="TEST99", hours=1, interval_minutes=30)
        assert result.record_count == 2
        assert result.records["station_id"].iloc[0] == "TEST99"

    def test_value_ranges(self):
        """Test that generated values are in reasonable ranges."""
        result = self.collector.collect(hours=48, interval_minutes=60)
        df = result.records

        assert df["ph"].between(0, 14).all()
        assert df["do"].between(0, 20).all()
        assert df["temperature"].between(-5, 45).all()

    def test_anomaly_injection(self):
        """Test that anomalies are occasionally generated."""
        # Generate a lot of data to increase chance of anomalies
        result = self.collector.collect(hours=240, interval_minutes=60)
        df = result.records

        # Some values should be outside normal ranges (anomalies)
        normal_ph = df[(df["ph"] >= 6.5) & (df["ph"] <= 8.5)]
        assert len(normal_ph) < len(df)  # Not all values are normal


class TestManualCollector:
    """Tests for manual data entry."""

    def setup_method(self):
        self.collector = ManualCollector()

    def test_valid_record(self):
        """Test adding a valid manual record."""
        record = {
            "station_id": "ST001",
            "collection_time": "2026-05-01 10:00:00",
            "ph": 7.2,
            "do": 6.5,
        }
        result = self.collector.collect(record)
        assert result.success
        assert result.record_count == 1

    def test_missing_station_id(self):
        """Test validation catches missing station_id."""
        result = self.collector.collect({"ph": 7.2})
        assert not result.success
        assert "station_id" in result.message

    def test_batch_records(self):
        """Test batch record entry."""
        records = [
            {"station_id": "ST001", "collection_time": "2026-05-01 10:00:00", "ph": 7.2},
            {"station_id": "ST002", "collection_time": "2026-05-01 11:00:00", "ph": 7.5},
        ]
        result = self.collector.collect_batch(records)
        assert result.success
        assert result.record_count == 2

    def test_empty_batch(self):
        """Test error handling for empty batch."""
        result = self.collector.collect_batch([])
        assert not result.success
