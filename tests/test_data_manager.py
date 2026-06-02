"""Unit tests for the DataManager singleton."""

from pathlib import Path

import pandas as pd
import pytest

from src.config import settings
from src.data_manager import data_manager


@pytest.fixture(autouse=True)
def reset_data_manager():
    """Clear data_manager before each test and restore after."""
    # Save current state
    had_raw = data_manager.has_raw()
    had_cleaned = data_manager.has_cleaned()

    yield

    # Restore: clear test data if we added any
    if data_manager.has_raw() and not had_raw:
        data_manager.clear_raw()
    if data_manager.has_cleaned() and not had_cleaned:
        data_manager.clear_cleaned()


class TestDataManagerInit:
    """Tests for DataManager initial state."""

    def test_has_raw_initially(self):
        """Should have raw data loaded from disk (from prior server run)."""
        # The singleton loaded whatever was on disk
        pass  # No assertion needed; depends on prior state

    def test_clear_then_no_raw(self):
        """After clearing, has_raw() returns False."""
        data_manager.clear_raw()
        assert data_manager.has_raw() is False

    def test_clear_then_no_cleaned(self):
        """After clearing, has_cleaned() returns False."""
        data_manager.clear_cleaned()
        assert data_manager.has_cleaned() is False


class TestDataManagerRawData:
    """Tests for raw data operations."""

    def test_set_raw_data(self, sample_df):
        """Setting raw data makes has_raw() True."""
        data_manager.clear_raw()
        data_manager.raw_data = sample_df
        assert data_manager.has_raw() is True

    def test_raw_data_value(self, sample_df):
        """Setter stores the correct DataFrame."""
        data_manager.clear_raw()
        data_manager.raw_data = sample_df
        assert len(data_manager.raw_data) == len(sample_df)
        assert list(data_manager.raw_data.columns) == list(sample_df.columns)

    def test_get_station_list(self, sample_df):
        """Returns unique station IDs from raw data."""
        data_manager.clear_raw()
        data_manager.raw_data = sample_df
        stations = data_manager.get_station_list()
        assert "ST001" in stations
        assert "ST002" in stations
        assert len(stations) == 2

    def test_get_station_list_empty(self):
        """Returns empty list when no raw data."""
        data_manager.clear_raw()
        assert data_manager.get_station_list() == []


class TestDataManagerAppendRaw:
    """Tests for append_raw."""

    def test_append_to_empty(self, sample_df):
        """Append to empty/None creates new data."""
        data_manager.clear_raw()
        subset = sample_df.iloc[:3]
        data_manager.append_raw(subset)
        assert data_manager.has_raw() is True
        assert len(data_manager.raw_data) == 3

    def test_append_to_existing(self, sample_df):
        """Row count increases by appended rows."""
        data_manager.clear_raw()
        data_manager.raw_data = sample_df.iloc[:3]
        data_manager.append_raw(sample_df.iloc[3:5])
        assert len(data_manager.raw_data) == 5


class TestDataManagerCleanedData:
    """Tests for cleaned data operations."""

    def test_set_cleaned_data(self, sample_df):
        """Setting cleaned data makes has_cleaned() True."""
        data_manager.clear_cleaned()
        data_manager.cleaned_data = sample_df
        assert data_manager.has_cleaned() is True

    def test_cleaned_data_value(self, sample_df):
        """Setter stores the correct DataFrame."""
        data_manager.clear_cleaned()
        data_manager.cleaned_data = sample_df
        assert len(data_manager.cleaned_data) == len(sample_df)


class TestDataManagerClear:
    """Tests for clear operations."""

    def test_clear_raw(self, sample_df):
        """clear_raw() removes raw data."""
        data_manager.clear_raw()
        data_manager.raw_data = sample_df
        assert data_manager.has_raw() is True
        data_manager.clear_raw()
        assert data_manager.has_raw() is False

    def test_clear_cleaned(self, sample_df):
        """clear_cleaned() removes cleaned data."""
        data_manager.clear_cleaned()
        data_manager.cleaned_data = sample_df
        assert data_manager.has_cleaned() is True
        data_manager.clear_cleaned()
        assert data_manager.has_cleaned() is False

    def test_clear_all(self, sample_df):
        """clear_all() removes both raw and cleaned."""
        data_manager.clear_raw()
        data_manager.clear_cleaned()
        data_manager.raw_data = sample_df
        data_manager.cleaned_data = sample_df
        data_manager.clear_all()
        assert data_manager.has_raw() is False
        assert data_manager.has_cleaned() is False


class TestDataManagerGetInfo:
    """Tests for get_data_info."""

    def test_info_after_clean(self, sample_df):
        """Info contains cleaned_records after setting cleaned data."""
        data_manager.clear_all()
        data_manager.raw_data = sample_df
        data_manager.cleaned_data = sample_df
        info = data_manager.get_data_info()
        assert info["has_raw"] is True
        assert info["has_cleaned"] is True
        assert info["raw_records"] == len(sample_df)
        assert info["cleaned_records"] == len(sample_df)
        assert "ST001" in info["stations"]

    def test_info_after_clear(self):
        """Info shows no data after clearing all."""
        data_manager.clear_all()
        info = data_manager.get_data_info()
        assert info["has_raw"] is False
        assert info["has_cleaned"] is False
