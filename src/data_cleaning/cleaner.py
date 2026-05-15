"""Data cleaning pipeline for water quality data preprocessing.

Provides a configurable cleaning pipeline that handles:
- Duplicate removal
- Missing value handling (drop, interpolate, fill with mean/median)
- Outlier detection (IQR method, Z-Score method)
- Data normalization (Min-Max, Z-Score)
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class CleaningReport:
    """Detailed report of the cleaning operation."""
    total_records: int = 0
    duplicates_removed: int = 0
    missing_handled: int = 0
    outliers_removed: int = 0
    records_after: int = 0
    columns_cleaned: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class DataCleaner:
    """Configurable data cleaning pipeline for water quality data.

    Supports multiple strategies for handling common data quality issues,
    configurable via CleaningConfig.
    """

    # Columns that should be cleaned (numeric water quality indicators)
    NUMERIC_INDICATORS = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.report = CleaningReport()

    def clean(self, df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        """Execute the full cleaning pipeline on a DataFrame.

        Args:
            df: Raw water quality data.

        Returns:
            Tuple of (cleaned DataFrame, CleaningReport).
        """
        self.report = CleaningReport(total_records=len(df))
        df = df.copy()

        # Step 1: Remove duplicates
        if self.config.get("remove_duplicates", True):
            df = self._remove_duplicates(df)

        # Step 2: Handle missing values
        missing_strategy = self.config.get("handle_missing", "interpolate")
        df = self._handle_missing(df, missing_strategy)

        # Step 3: Detect and remove outliers
        outlier_method = self.config.get("outlier_method", "iqr")
        if outlier_method != "none":
            df = self._remove_outliers(df, outlier_method)

        # Step 4: Normalize data if configured
        if self.config.get("normalize", False):
            norm_method = self.config.get("normalize_method", "minmax")
            df = self._normalize(df, norm_method)

        # Determine which columns were actually cleaned
        indicators_cleaned = [c for c in self.NUMERIC_INDICATORS if c in df.columns]
        self.report.columns_cleaned = indicators_cleaned

        self.report.records_after = len(df)
        self.report.details["config_used"] = self.config

        # Build summary
        self.report.details["summary"] = (
            f"Cleaned {self.report.total_records} records: "
            f"removed {self.report.duplicates_removed} duplicates, "
            f"handled {self.report.missing_handled} missing values, "
            f"removed {self.report.outliers_removed} outliers. "
            f"Result: {self.report.records_after} records."
        )

        return df, self.report

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows based on all columns."""
        before = len(df)
        df = df.drop_duplicates()
        self.report.duplicates_removed = before - len(df)
        return df

    def _handle_missing(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """Handle missing values in numeric indicator columns."""
        indicators = [c for c in self.NUMERIC_INDICATORS if c in df.columns]
        before_missing = df[indicators].isna().sum().sum()

        if strategy == "drop":
            df = df.dropna(subset=indicators)
        elif strategy == "fill_mean":
            for col in indicators:
                df[col] = df[col].fillna(df[col].mean())
        elif strategy == "fill_median":
            for col in indicators:
                df[col] = df[col].fillna(df[col].median())
        elif strategy == "interpolate":
            df[indicators] = df[indicators].interpolate(method="linear")
            # Forward fill any remaining NaNs at the start
            df[indicators] = df[indicators].ffill()
            # Backward fill any remaining NaNs at the end
            df[indicators] = df[indicators].bfill()

        after_missing = df[indicators].isna().sum().sum()
        self.report.missing_handled = before_missing - after_missing
        return df

    def _remove_outliers(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        """Detect and remove outliers using specified method."""
        indicators = [c for c in self.NUMERIC_INDICATORS if c in df.columns]
        before = len(df)

        outlier_mask = pd.Series(False, index=df.index)

        for col in indicators:
            col_data = df[col].dropna()
            if len(col_data) < 4:
                continue

            if method == "iqr":
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                iqr = Q3 - Q1
                threshold = self.config.get("outlier_threshold", 1.5)
                lower = Q1 - threshold * iqr
                upper = Q3 + threshold * iqr
                col_outliers = (df[col] < lower) | (df[col] > upper)
                outlier_mask = outlier_mask | col_outliers.fillna(False)

            elif method == "zscore":
                mean = col_data.mean()
                std = col_data.std()
                if std > 0:
                    threshold = self.config.get("outlier_threshold", 3)
                    z_scores = (df[col] - mean) / std
                    col_outliers = z_scores.abs() > threshold
                    outlier_mask = outlier_mask | col_outliers.fillna(False)

        df = df[~outlier_mask]
        self.report.outliers_removed = before - len(df)
        return df

    def _normalize(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        """Normalize numeric columns to a standard scale."""
        indicators = [c for c in self.NUMERIC_INDICATORS if c in df.columns]
        df = df.copy()

        for col in indicators:
            col_data = df[col].dropna()
            if len(col_data) < 2:
                continue

            if method == "minmax":
                min_val = col_data.min()
                max_val = col_data.max()
                if max_val > min_val:
                    df[col] = (df[col] - min_val) / (max_val - min_val)
            elif method == "zscore":
                mean = col_data.mean()
                std = col_data.std()
                if std > 0:
                    df[col] = (df[col] - mean) / std

        return df

    def get_report_summary(self) -> str:
        """Get a human-readable summary of the cleaning operation."""
        return self.report.details.get("summary", "No cleaning performed yet.")
