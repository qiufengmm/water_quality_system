"""CSV/Excel file data collector for importing historical water quality data."""

from pathlib import Path
from typing import Optional

import pandas as pd

from .base import BaseCollector, CollectResult


class CsvCollector(BaseCollector):
    """Collector for importing water quality data from CSV and Excel files.

    Supports automatic column name mapping and format detection.
    """

    # Standard column name mapping (display name -> internal name)
    COLUMN_MAP = {
        "监测时间": "collection_time", "时间": "collection_time", "采集时间": "collection_time",
        "站点": "station_id", "点位": "station_id", "监测点": "station_id", "站号": "station_id",
        "pH": "ph", "PH": "ph", "酸碱度": "ph",
        "溶解氧": "do", "DO": "do",
        "氨氮": "nh3n", "NH3N": "nh3n", "nh3_n": "nh3n",
        "浊度": "turbidity", "NTU": "turbidity",
        "温度": "temperature", "水温": "temperature",
        "COD": "cod", "化学需氧量": "cod",
        "总磷": "total_phosphorus", "TP": "total_phosphorus",
    }

    def __init__(self):
        super().__init__("csv_importer")

    def collect(self, file_path: str, **kwargs) -> CollectResult:
        """Import data from CSV or Excel file.

        Args:
            file_path: Path to the CSV or Excel file.

        Returns:
            CollectResult with imported data.
        """
        path = Path(file_path)
        if not path.exists():
            return CollectResult(
                success=False,
                message=f"File not found: {file_path}",
                errors=[f"File does not exist: {file_path}"]
            )

        try:
            # Read file based on extension
            suffix = path.suffix.lower()
            if suffix == ".csv":
                df = pd.read_csv(file_path, encoding=kwargs.get("encoding", "utf-8-sig"))
            elif suffix in (".xlsx", ".xls"):
                df = pd.read_excel(file_path)
            else:
                return CollectResult(
                    success=False,
                    message=f"Unsupported file format: {suffix}",
                    errors=[f"Only .csv, .xlsx, .xls files are supported"]
                )

            # Standardize column names
            df = self._standardize_columns(df)

            # Parse datetime column
            if "collection_time" in df.columns:
                df["collection_time"] = pd.to_datetime(
                    df["collection_time"], errors="coerce"
                )

            self._data = df
            errors = self.validate(df)

            return CollectResult(
                success=len(errors) == 0,
                records=df,
                record_count=len(df),
                message=f"Successfully imported {len(df)} records from {path.name}",
                errors=errors
            )

        except Exception as e:
            return CollectResult(
                success=False,
                message=f"Failed to read file: {str(e)}",
                errors=[str(e)]
            )

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map Chinese/non-standard column names to internal standard names."""
        df = df.rename(columns=lambda c: self.COLUMN_MAP.get(c.strip(), c.strip()))
        # Keep unknown columns, don't drop them
        return df

    def collect_batch(self, file_paths: list[str]) -> list[CollectResult]:
        """Import multiple files at once.

        Args:
            file_paths: List of file paths to import.

        Returns:
            List of CollectResult for each file.
        """
        return [self.collect(fp) for fp in file_paths]
