"""Alert API routes for water quality monitoring."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends

from src.config import settings
from src.data_manager import data_manager
from src.alerting import alert_engine

router = APIRouter()


@router.get("/alert/rules")
async def get_alert_rules():
    """Get all alert rules with current thresholds."""
    return {
        "rules": alert_engine.get_rules(),
    }


@router.put("/alert/rules")
async def update_alert_rules(rules_data: list[dict]):
    """Update alert rules configuration."""
    try:
        alert_engine.update_rules(rules_data)
        return {"message": "Rules updated", "rules": alert_engine.get_rules()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update rules: {str(e)}")


@router.post("/alert/check")
async def check_alerts():
    """Run alert check on current raw data."""
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No raw data loaded.")

    df = data_manager.raw_data
    alerts = alert_engine.check_and_save(df)

    # Count by severity
    severity_count = {"critical": 0, "warning": 0, "info": 0}
    for a in alerts:
        severity_count[a.severity] = severity_count.get(a.severity, 0) + 1

    return {
        "checked_records": len(df),
        "alerts_triggered": len(alerts),
        "severity_summary": severity_count,
        "alerts": [
            {
                "station_id": a.station_id,
                "indicator": a.indicator,
                "value": a.value,
                "rule": a.rule,
                "severity": a.severity,
                "timestamp": a.timestamp,
            }
            for a in alerts
        ],
    }


@router.get("/alert/history")
async def get_alert_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: str = Query(None, pattern="^(critical|warning|info)?$"),
):
    """Get paginated alert history."""
    return alert_engine.get_history(page=page, page_size=page_size, severity=severity)


@router.delete("/alert/history")
async def clear_alert_history():
    """Clear all alert history records."""
    alert_engine.clear_history()
    return {"message": "Alert history cleared"}
