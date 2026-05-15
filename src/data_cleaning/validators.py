"""Water quality data validators based on environmental standards."""

from dataclasses import dataclass, field

import pandas as pd


# GB 3838-2002 Surface Water Quality Standards
WATER_QUALITY_STANDARDS = {
    "ph": {"min": 6.0, "max": 9.0, "description": "pH value (6-9 for Class I-V)"},
    "do": {"min": 2.0, "max": 15.0, "description": "Dissolved oxygen ≥2 mg/L"},
    "nh3n": {"min": 0, "max": 2.0, "description": "Ammonia nitrogen ≤2.0 mg/L"},
    "turbidity": {"min": 0, "max": 100, "description": "Turbidity 0-100 NTU"},
    "temperature": {"min": -5, "max": 45, "description": "Water temperature -5~45°C"},
    "cod": {"min": 0, "max": 50, "description": "COD ≤50 mg/L"},
    "total_phosphorus": {"min": 0, "max": 0.5, "description": "Total phosphorus ≤0.5 mg/L"},
}

# Warning thresholds (approaching standard limits)
WARNING_THRESHOLDS = {
    "ph": {"min": 6.5, "max": 8.5},
    "do": {"min": 3.0},
    "nh3n": {"max": 1.5},
    "cod": {"max": 30},
}


@dataclass
class ValidationReport:
    """Detailed validation report."""
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    errors: list[str] = field(default_factory=list)
    column_status: dict = field(default_factory=dict)


class WaterQualityValidator:
    """Validator for water quality data against environmental standards.

    Validates each indicator against the Chinese Surface Water Quality
    Standards (GB 3838-2002) acceptable ranges.
    """

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.standards = WATER_QUALITY_STANDARDS
        self.warning_thresholds = WARNING_THRESHOLDS

    def validate_record(self, record: dict) -> ValidationReport:
        """Validate a single water quality record.

        Args:
            record: Dictionary containing water quality data.

        Returns:
            ValidationReport with check results.
        """
        report = ValidationReport()
        df = pd.DataFrame([record])
        return self._validate_dataframe(df)

    def validate_dataframe(self, df: pd.DataFrame) -> ValidationReport:
        """Validate an entire DataFrame of water quality data.

        Args:
            df: DataFrame with water quality columns.

        Returns:
            ValidationReport with aggregated results.
        """
        return self._validate_dataframe(df)

    def _validate_dataframe(self, df: pd.DataFrame) -> ValidationReport:
        """Core validation logic for DataFrames."""
        report = ValidationReport()

        for column in df.columns:
            if column in ("station_id", "collection_time"):
                continue

            standard = self.standards.get(column)
            if standard is None:
                continue

            col_data = df[column].dropna()
            if col_data.empty:
                continue

            col_errors = []
            col_warnings = 0

            # Range check
            out_of_range = col_data[
                (col_data < standard["min"]) | (col_data > standard["max"])
            ]
            if not out_of_range.empty:
                col_errors.append(
                    f"{column}: {len(out_of_range)} values outside "
                    f"[{standard['min']}, {standard['max']}]"
                )

            # Warning threshold check
            warning = self.warning_thresholds.get(column, {})
            if "min" in warning:
                col_warnings += len(col_data[col_data < warning["min"]])
            if "max" in warning:
                col_warnings += len(col_data[col_data > warning["max"]])

            report.total_checks += 1
            if col_errors:
                report.errors.extend(col_errors)
            else:
                report.passed += 1

            report.warnings += col_warnings
            report.column_status[column] = {
                "passed": len(col_errors) == 0,
                "errors": col_errors,
                "warnings": col_warnings,
            }

        return report
