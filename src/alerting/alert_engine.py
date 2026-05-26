"""Alert engine for water quality monitoring.

Provides rule-based alert checking against water quality data,
with configurable thresholds and severity levels based on
GB 3838-2002 Chinese Surface Water Quality Standards.
"""

import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import settings


@dataclass
class AlertRule:
    """Water quality alert rule definition."""
    indicator: str          # e.g. "ph", "do", "nh3n"
    operator: str           # ">" or "<"
    threshold: float
    severity: str           # "info", "warning", "critical"
    label: str = ""         # Human-readable indicator name
    enabled: bool = True


@dataclass
class AlertRecord:
    """Record of a triggered alert."""
    station_id: str
    indicator: str
    value: float
    rule: str               # description like "pH < 6.0"
    severity: str
    timestamp: str
    status: str = "active"  # "active", "acknowledged", "resolved"


class AlertEngine:
    """Engine for checking water quality data against alert rules.

    Maintains a list of AlertRules and can check DataFrames against them,
    producing AlertRecords. History is persisted to a CSV file.
    """

    # Default rules based on GB 3838-2002 Class III standards
    DEFAULT_RULES = [
        AlertRule("ph", "<", 6.0, "critical", "pH"),
        AlertRule("ph", ">", 9.0, "critical", "pH"),
        AlertRule("do", "<", 2.0, "critical", "溶解氧(DO)"),
        AlertRule("do", "<", 3.0, "warning", "溶解氧(DO)"),
        AlertRule("nh3n", ">", 2.0, "critical", "氨氮(NH3N)"),
        AlertRule("nh3n", ">", 1.0, "warning", "氨氮(NH3N)"),
        AlertRule("cod", ">", 40.0, "critical", "化学需氧量(COD)"),
        AlertRule("cod", ">", 20.0, "warning", "化学需氧量(COD)"),
        AlertRule("turbidity", ">", 10.0, "warning", "浊度"),
        AlertRule("turbidity", ">", 5.0, "info", "浊度"),
        AlertRule("total_phosphorus", ">", 0.4, "critical", "总磷"),
        AlertRule("total_phosphorus", ">", 0.2, "warning", "总磷"),
    ]

    def __init__(self, rules: Optional[list[AlertRule]] = None):
        self.rules = rules or [AlertRule(**r) if isinstance(r, dict) else r
                               for r in self.DEFAULT_RULES]
        self._history_path = Path(settings.data_dir) / "alert_history.csv"

    def check_dataframe(self, df: pd.DataFrame) -> list[AlertRecord]:
        """Check all records in a DataFrame against all enabled rules.

        Args:
            df: Water quality data with indicator columns and station_id.

        Returns:
            List of AlertRecord for each triggered alert.
        """
        alerts: list[AlertRecord] = []
        enabled_rules = [r for r in self.rules if r.enabled]
        now = datetime.now().isoformat(timespec="seconds")

        for rule in enabled_rules:
            if rule.indicator not in df.columns:
                continue

            col_data = df[rule.indicator].dropna()

            if rule.operator == ">":
                triggered = col_data[col_data > rule.threshold]
            else:
                triggered = col_data[col_data < rule.threshold]

            for idx in triggered.index:
                station = df.loc[idx, "station_id"] if "station_id" in df.columns else "unknown"
                alerts.append(AlertRecord(
                    station_id=str(station),
                    indicator=rule.indicator,
                    value=float(triggered[idx]),
                    rule=f"{rule.label} {rule.operator} {rule.threshold}",
                    severity=rule.severity,
                    timestamp=now,
                ))

        return alerts

    def check_and_save(self, df: pd.DataFrame) -> list[AlertRecord]:
        """Check data and persist new alerts to history CSV.

        Args:
            df: Water quality data to check.

        Returns:
            List of new AlertRecord instances.
        """
        new_alerts = self.check_dataframe(df)

        if new_alerts:
            self._save_alerts(new_alerts)

        return new_alerts

    def _save_alerts(self, alerts: list[AlertRecord]):
        """Append alert records to the history CSV file."""
        file_exists = self._history_path.exists()
        with open(self._history_path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "station_id", "indicator", "value", "rule", "severity", "timestamp", "status"
            ])
            if not file_exists:
                writer.writeheader()
            for a in alerts:
                writer.writerow(asdict(a))

    def get_history(self, page: int = 1, page_size: int = 20,
                    severity: Optional[str] = None) -> dict:
        """Get paginated alert history.

        Returns:
            dict with total, page, page_size, records
        """
        if not self._history_path.exists():
            return {"total": 0, "page": page, "page_size": page_size, "records": []}

        records = []
        with open(self._history_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if severity and row.get("severity") != severity:
                    continue
                records.append(row)

        # Sort by timestamp descending
        records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)

        total = len(records)
        start = (page - 1) * page_size
        end = start + page_size
        page_records = records[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "records": page_records,
        }

    def clear_history(self):
        """Delete all alert history."""
        if self._history_path.exists():
            self._history_path.unlink()

    def get_rules(self) -> list[dict]:
        """Get all rules as serializable dicts."""
        return [asdict(r) for r in self.rules]

    def update_rules(self, rules_data: list[dict]):
        """Replace all rules with new data."""
        self.rules = []
        for r in rules_data:
            # Ensure all required fields
            rule = AlertRule(
                indicator=r.get("indicator", "ph"),
                operator=r.get("operator", "<"),
                threshold=float(r.get("threshold", 0)),
                severity=r.get("severity", "warning"),
                label=r.get("label", ""),
                enabled=r.get("enabled", True),
            )
            self.rules.append(rule)


# Singleton
alert_engine = AlertEngine()
