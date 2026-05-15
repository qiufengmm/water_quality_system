"""Data transformers for standardizing water quality data format."""

import re
from datetime import datetime

import pandas as pd


class DataTransformer:
    """Transform and standardize water quality data format.

    Handles unit conversion, time format unification, and column
    name standardization.
    """

    # Unit conversion factors
    UNIT_CONVERSIONS = {
        "mg_to_μg": 1000,
        "μg_to_mg": 0.001,
        "celsius_to_fahrenheit": lambda c: c * 9 / 5 + 32,
        "fahrenheit_to_celsius": lambda f: (f - 32) * 5 / 9,
    }

    # Common date format patterns
    DATE_PATTERNS = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]

    def __init__(self):
        self.transform_log: list[str] = []

    def standardize_datetime(self, df: pd.DataFrame,
                             column: str = "collection_time") -> pd.DataFrame:
        """Unify datetime column to standard format.

        Args:
            df: Input DataFrame.
            column: Datetime column name.

        Returns:
            DataFrame with standardized datetime.
        """
        if column not in df.columns:
            return df

        df = df.copy()

        # Try parsing with known patterns
        if df[column].dtype == "object":
            parsed = pd.to_datetime(df[column], errors="coerce")
            success_count = parsed.notna().sum()
            df[column] = parsed
            self.transform_log.append(
                f"Standardized {success_count}/{len(df)} datetime values"
            )

        return df

    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to snake_case.

        Args:
            df: Input DataFrame.

        Returns:
            DataFrame with standardized column names.
        """
        df = df.copy()
        rename_map = {}

        for col in df.columns:
            new_name = self._to_snake_case(col)
            if new_name != col:
                rename_map[col] = new_name

        if rename_map:
            df = df.rename(columns=rename_map)
            self.transform_log.append(
                f"Renamed columns: {rename_map}"
            )

        return df

    def convert_units(self, df: pd.DataFrame,
                      conversions: dict[str, str]) -> pd.DataFrame:
        """Apply unit conversions to specified columns.

        Args:
            df: Input DataFrame.
            conversions: Dict of {column: conversion_key}.

        Returns:
            DataFrame with converted units.
        """
        df = df.copy()

        for column, conversion in conversions.items():
            if column not in df.columns:
                continue

            if conversion == "mg_to_μg":
                df[column] = df[column] * 1000
            elif conversion == "μg_to_mg":
                df[column] = df[column] / 1000
            elif conversion == "celsius_to_fahrenheit":
                df[column] = df[column] * 9 / 5 + 32
            elif conversion == "fahrenheit_to_celsius":
                df[column] = (df[column] - 32) * 5 / 9

            self.transform_log.append(
                f"Converted {column} using {conversion}"
            )

        return df

    def _to_snake_case(self, name: str) -> str:
        """Convert a column name to snake_case."""
        name = re.sub(r"[^a-zA-Z0-9一-鿿_]", "_", str(name))
        name = re.sub(r"([A-Z])", r"_\1", name).lower()
        name = re.sub(r"__+", "_", name)
        name = name.strip("_")
        return name

    def get_log(self) -> list[str]:
        """Get transformation log entries."""
        return self.transform_log
