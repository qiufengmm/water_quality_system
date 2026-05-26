"""Data persistence and management layer.

Provides file-based persistence for water quality data, supporting
save/load operations that survive server restarts.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import settings


class DataManager:
    """Manages water quality data with file-based persistence.

    Automatically saves data to CSV on each write operation and
    loads from disk on startup, ensuring data survives restarts.
    """

    def __init__(self):
        self._raw_data: Optional[pd.DataFrame] = None
        self._cleaned_data: Optional[pd.DataFrame] = None
        self._raw_path = Path(settings.raw_data_dir) / "_current_raw.csv"
        self._cleaned_path = Path(settings.cleaned_data_dir) / "_current_cleaned.csv"
        self._metadata_path = Path(settings.raw_data_dir) / "_metadata.json"
        self._load_from_disk()

    # ── Raw Data ──────────────────────────────────────────────

    @property
    def raw_data(self) -> Optional[pd.DataFrame]:
        return self._raw_data

    @raw_data.setter
    def raw_data(self, df: Optional[pd.DataFrame]):
        self._raw_data = df
        self._save_raw()

    def append_raw(self, df: pd.DataFrame):
        """Append new records to existing raw data."""
        if self._raw_data is not None and not self._raw_data.empty:
            self._raw_data = pd.concat([self._raw_data, df], ignore_index=True)
        else:
            self._raw_data = df
        self._save_raw()

    @property
    def cleaned_data(self) -> Optional[pd.DataFrame]:
        return self._cleaned_data

    @cleaned_data.setter
    def cleaned_data(self, df: Optional[pd.DataFrame]):
        self._cleaned_data = df
        self._save_cleaned()

    def has_raw(self) -> bool:
        return self._raw_data is not None and not self._raw_data.empty

    def has_cleaned(self) -> bool:
        return self._cleaned_data is not None and not self._cleaned_data.empty

    def clear_raw(self):
        """Clear all raw data."""
        self._raw_data = None
        if self._raw_path.exists():
            self._raw_path.unlink()

    def clear_cleaned(self):
        """Clear all cleaned data."""
        self._cleaned_data = None
        if self._cleaned_path.exists():
            self._cleaned_path.unlink()

    def clear_all(self):
        """Clear all data."""
        self.clear_raw()
        self.clear_cleaned()

    # ── Persistence ───────────────────────────────────────────

    def _load_from_disk(self):
        """Load data from disk on startup."""
        try:
            if self._raw_path.exists():
                self._raw_data = pd.read_csv(
                    self._raw_path,
                    parse_dates=["collection_time"] if self._raw_path.stat().st_size > 0 else False,
                    encoding="utf-8-sig"
                )
        except Exception:
            self._raw_data = None

        try:
            if self._cleaned_path.exists():
                self._cleaned_data = pd.read_csv(
                    self._cleaned_path,
                    parse_dates=["collection_time"] if self._cleaned_path.stat().st_size > 0 else False,
                    encoding="utf-8-sig"
                )
        except Exception:
            self._cleaned_data = None

    def _save_raw(self):
        """Persist raw data to disk."""
        if self._raw_data is not None and not self._raw_data.empty:
            self._raw_path.parent.mkdir(parents=True, exist_ok=True)
            self._raw_data.to_csv(self._raw_path, index=False, encoding="utf-8-sig")
        elif self._raw_path.exists():
            self._raw_path.unlink()

    def _save_cleaned(self):
        """Persist cleaned data to disk."""
        if self._cleaned_data is not None and not self._cleaned_data.empty:
            self._cleaned_path.parent.mkdir(parents=True, exist_ok=True)
            self._cleaned_data.to_csv(self._cleaned_path, index=False, encoding="utf-8-sig")
        elif self._cleaned_path.exists():
            self._cleaned_path.unlink()

    # ── Utility ───────────────────────────────────────────────

    def get_station_list(self) -> list[str]:
        """Get unique station IDs from raw data."""
        if self._raw_data is None or "station_id" not in self._raw_data.columns:
            return []
        return list(self._raw_data["station_id"].dropna().unique())

    def get_data_info(self) -> dict:
        """Get metadata about currently loaded data."""
        info = {
            "has_raw": self.has_raw(),
            "has_cleaned": self.has_cleaned(),
        }
        if self.has_raw():
            info["raw_records"] = len(self._raw_data)
            info["raw_columns"] = list(self._raw_data.columns)
            info["stations"] = self.get_station_list()
            if "collection_time" in self._raw_data.columns:
                info["raw_date_range"] = [
                    str(self._raw_data["collection_time"].min()),
                    str(self._raw_data["collection_time"].max()),
                ]
        if self.has_cleaned():
            info["cleaned_records"] = len(self._cleaned_data)
        return info


data_manager = DataManager()
