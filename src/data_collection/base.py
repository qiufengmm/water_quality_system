"""Base collector interface for water quality data collection."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class CollectResult:
    """Standard result from a collection operation."""
    success: bool
    records: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    record_count: int = 0
    message: str = ""
    errors: list[str] = field(default_factory=list)
    collection_time: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.records.empty and self.record_count == 0:
            self.record_count = len(self.records)


class BaseCollector(ABC):
    """Abstract base class for all data collectors.

    All data source implementations must inherit from this class
    and implement the collect(), validate(), and save() methods.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name
        self._data: Optional[pd.DataFrame] = None

    @abstractmethod
    def collect(self, **kwargs) -> CollectResult:
        """Collect data from the source.

        Returns:
            CollectResult containing the collected data and status.
        """
        pass

    def validate(self, df: pd.DataFrame) -> list[str]:
        """Validate collected data format and content.

        Args:
            df: DataFrame to validate.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []
        required_cols = {"station_id", "collection_time"}
        missing = required_cols - set(df.columns)
        if missing:
            errors.append(f"Missing required columns: {missing}")

        if "ph" in df.columns and df["ph"].notna().any():
            invalid_ph = df[df["ph"].notna() & ((df["ph"] < 0) | (df["ph"] > 14))]
            if not invalid_ph.empty:
                errors.append(f"{len(invalid_ph)} records have pH values outside [0, 14]")

        return errors

    def save(self,
             df: pd.DataFrame,
             output_dir: str,
             filename: Optional[str] = None) -> str:
        """Save collected data to CSV file.

        Args:
            df: DataFrame to save.
            output_dir: Directory to save to.
            filename: Optional filename (auto-generated if not provided).

        Returns:
            Path to the saved file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.source_name}_{timestamp}.csv"

        output_path = Path(output_dir) / filename
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        return str(output_path)

    def get_data(self) -> Optional[pd.DataFrame]:
        """Get the currently loaded data."""
        return self._data
