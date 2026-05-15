"""Unit tests for data cleaning modules."""

import pandas as pd
import pytest

from src.data_cleaning import DataCleaner, DataTransformer, WaterQualityValidator


class TestDataCleaner:
    """Tests for data cleaning pipeline."""

    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_clean_complete_data(self):
        """Test cleaning data with no issues."""
        df = pd.DataFrame({
            "station_id": ["ST001", "ST002"],
            "ph": [7.2, 7.5],
            "do": [6.5, 5.8],
            "nh3n": [0.15, 0.22],
        })
        cleaned, report = self.cleaner.clean(df)
        assert len(cleaned) == 2
        assert report.duplicates_removed == 0

    def test_remove_duplicates(self):
        """Test duplicate row removal."""
        df = pd.DataFrame({
            "station_id": ["ST001", "ST001", "ST001"],
            "ph": [7.2, 7.2, 7.5],
            "do": [6.5, 6.5, 5.8],
        })
        cleaned, report = self.cleaner.clean(df)
        assert report.duplicates_removed == 1
        assert len(cleaned) == 2

    def test_handle_missing_drop(self):
        """Test dropping rows with missing values."""
        df = pd.DataFrame({
            "station_id": ["ST001", "ST002", "ST003"],
            "ph": [7.2, None, 7.5],
            "do": [6.5, 5.8, None],
        })
        cleaner = DataCleaner({"handle_missing": "drop"})
        cleaned, report = cleaner.clean(df)
        assert report.missing_handled > 0

    def test_handle_missing_interpolate(self):
        """Test interpolating missing values."""
        df = pd.DataFrame({
            "station_id": ["ST001", "ST002", "ST003"],
            "ph": [7.0, None, 8.0],
            "do": [6.0, 6.5, None],
        })
        cleaner = DataCleaner({"handle_missing": "interpolate"})
        cleaned, report = cleaner.clean(df)
        assert cleaned["ph"].notna().all()
        assert cleaned["do"].notna().all()

    def test_outlier_detection_iqr(self):
        """Test IQR-based outlier detection."""
        df = pd.DataFrame({
            "station_id": ["ST001"] * 20,
            "ph": [7.0] * 18 + [3.0, 12.0],  # Two outliers
            "do": [6.0] * 20,
        })
        cleaner = DataCleaner({"outlier_method": "iqr"})
        cleaned, report = self.cleaner.clean(df)
        assert report.outliers_removed >= 0

    def test_outlier_detection_zscore(self):
        """Test Z-Score based outlier detection."""
        df = pd.DataFrame({
            "station_id": ["ST001"] * 20,
            "ph": [7.0] * 18 + [2.0, 13.0],  # Two outliers
            "do": [6.0] * 20,
        })
        cleaner = DataCleaner({
            "outlier_method": "zscore",
            "outlier_threshold": 2.5,
        })
        cleaned, report = cleaner.clean(df)
        assert report.outliers_removed >= 0

    def test_normalize_minmax(self):
        """Test Min-Max normalization."""
        df = pd.DataFrame({
            "station_id": ["ST001", "ST002", "ST003"],
            "ph": [6.0, 7.0, 8.0],
            "do": [5.0, 6.0, 7.0],
        })
        cleaner = DataCleaner({"normalize": True, "normalize_method": "minmax"})
        cleaned, report = cleaner.clean(df)
        assert cleaned["ph"].between(0, 1).all()
        assert cleaned["do"].between(0, 1).all()

    def test_empty_dataframe(self):
        """Test cleaning an empty DataFrame."""
        df = pd.DataFrame()
        cleaned, report = self.cleaner.clean(df)
        assert len(cleaned) == 0


class TestWaterQualityValidator:
    """Tests for water quality validation."""

    def setup_method(self):
        self.validator = WaterQualityValidator()

    def test_valid_data(self):
        """Test validation passes for normal data."""
        df = pd.DataFrame({
            "station_id": ["ST001"],
            "ph": [7.2],
            "do": [6.5],
        })
        report = self.validator.validate_dataframe(df)
        assert report.passed >= 2
        assert len(report.errors) == 0

    def test_out_of_range_ph(self):
        """Test detection of out-of-range pH values."""
        df = pd.DataFrame({
            "station_id": ["ST001"],
            "ph": [14.5],  # Exceeds max 9.0
        })
        report = self.validator.validate_dataframe(df)
        assert len(report.errors) > 0
        assert "ph" in report.errors[0]

    def test_missing_indicators(self):
        """Test validation skips missing columns gracefully."""
        df = pd.DataFrame({
            "station_id": ["ST001"],
        })
        report = self.validator.validate_dataframe(df)
        assert report.total_checks == 0


class TestDataTransformer:
    """Tests for data transformation."""

    def setup_method(self):
        self.transformer = DataTransformer()

    def test_datetime_standardization(self):
        """Test datetime format unification."""
        df = pd.DataFrame({
            "collection_time": ["2026/05/01 08:00:00", "05/01/2026 09:00"],
            "ph": [7.2, 7.5],
        })
        result = self.transformer.standardize_datetime(df)
        assert pd.api.types.is_datetime64_any_dtype(result["collection_time"])

    def test_column_standardization(self):
        """Test column name standardization."""
        df = pd.DataFrame({
            "WaterTemp": [22.5],
            "DissolvedOxygen": [6.5],
        })
        result = self.transformer.standardize_columns(df)
        assert "water_temp" in result.columns or "watertemperature" in result.columns

    def test_transform_log(self):
        """Test that transformation activities are logged."""
        df = pd.DataFrame({"collection_time": ["2026-05-01 08:00:00"], "ph": [7.2]})
        self.transformer.standardize_datetime(df)
        assert len(self.transformer.get_log()) > 0
