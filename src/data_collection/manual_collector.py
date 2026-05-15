"""Manual data entry collector for laboratory test results."""

from datetime import datetime
from typing import Optional

import pandas as pd

from .base import BaseCollector, CollectResult


class ManualCollector(BaseCollector):
    """Collector for manually entered water quality data (lab test results).

    Supports single record entry and batch validation.
    """

    def __init__(self):
        super().__init__("manual_entry")

    def collect(self, record: dict, **kwargs) -> CollectResult:
        """Collect a single manually entered water quality record.

        Args:
            record: Dictionary with water quality data fields.

        Returns:
            CollectResult with validated record.
        """
        # Ensure required fields
        if "station_id" not in record:
            return CollectResult(
                success=False,
                message="Missing required field: station_id",
                errors=["station_id is required"]
            )

        if "collection_time" not in record:
            record["collection_time"] = datetime.now()

        df = pd.DataFrame([record])

        # Parse datetime if string
        if isinstance(record.get("collection_time"), str):
            df["collection_time"] = pd.to_datetime(
                df["collection_time"], errors="coerce"
            )

        errors = self.validate(df)
        if errors:
            return CollectResult(
                success=False,
                records=df,
                message="Validation failed",
                errors=errors
            )

        self._data = df
        return CollectResult(
            success=True,
            records=df,
            record_count=1,
            message="Manual record validated successfully"
        )

    def collect_batch(self, records: list[dict]) -> CollectResult:
        """Collect multiple manually entered records at once.

        Args:
            records: List of record dictionaries.

        Returns:
            CollectResult with all validated records.
        """
        if not records:
            return CollectResult(
                success=False,
                message="No records provided",
                errors=["Empty record list"]
            )

        df = pd.DataFrame(records)

        # Parse datetime columns
        if "collection_time" in df.columns:
            df["collection_time"] = pd.to_datetime(
                df["collection_time"], errors="coerce"
            )

        errors = self.validate(df)
        self._data = df

        return CollectResult(
            success=len(errors) == 0,
            records=df,
            record_count=len(df),
            message=f"Validated {len(df)} manual records",
            errors=errors
        )
