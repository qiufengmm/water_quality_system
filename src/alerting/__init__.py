"""Alerting module for water quality monitoring.

Provides rule-based alert checking against GB 3838-2002 standards.
"""

from .alert_engine import AlertEngine, AlertRule, AlertRecord, alert_engine

__all__ = ["AlertEngine", "AlertRule", "AlertRecord", "alert_engine"]
