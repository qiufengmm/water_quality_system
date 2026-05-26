"""Data export API routes.

Provides CSV and JSON export of raw and cleaned data.
"""

from datetime import datetime
from io import StringIO
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.data_manager import data_manager
from src.config import settings

router = APIRouter()


def _to_csv_stream(df: pd.DataFrame, filename: str) -> StreamingResponse:
    """Convert DataFrame to CSV streaming response."""
    buf = StringIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _to_json_response(df: pd.DataFrame, filename: str):
    """Convert DataFrame to JSON list response."""
    result = df.copy()
    if "collection_time" in result.columns:
        result["collection_time"] = result["collection_time"].astype(str)
    records = result.replace({float("nan"): None}).to_dict(orient="records")
    return records


@router.get("/raw/csv")
async def export_raw_csv():
    """Export raw data as CSV file download."""
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No raw data available.")
    filename = f"raw_data_{datetime.now().strftime('%Y%m%d')}.csv"
    return _to_csv_stream(data_manager.raw_data, filename)


@router.get("/raw/json")
async def export_raw_json():
    """Export raw data as JSON."""
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No raw data available.")
    return _to_json_response(data_manager.raw_data, "raw_export.json")


@router.get("/cleaned/csv")
async def export_cleaned_csv():
    """Export cleaned data as CSV file download."""
    if not data_manager.has_cleaned():
        raise HTTPException(status_code=400, detail="No cleaned data available.")
    filename = f"cleaned_data_{datetime.now().strftime('%Y%m%d')}.csv"
    return _to_csv_stream(data_manager.cleaned_data, filename)


@router.get("/cleaned/json")
async def export_cleaned_json():
    """Export cleaned data as JSON."""
    if not data_manager.has_cleaned():
        raise HTTPException(status_code=400, detail="No cleaned data available.")
    return _to_json_response(data_manager.cleaned_data, "cleaned_export.json")


@router.get("/summary/csv")
async def export_summary_csv():
    """Export a statistical summary as CSV."""
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No data loaded.")

    df = data_manager.raw_data
    indicators = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]
    stats = []

    for col in indicators:
        if col in df.columns:
            col_data = df[col].dropna()
            if not col_data.empty:
                stats.append({
                    "indicator": col,
                    "min": round(float(col_data.min()), 2),
                    "max": round(float(col_data.max()), 2),
                    "mean": round(float(col_data.mean()), 2),
                    "std": round(float(col_data.std()), 2),
                    "count": int(col_data.count()),
                    "missing": int(df[col].isna().sum()),
                })

    stats_df = pd.DataFrame(stats)
    filename = f"summary_{datetime.now().strftime('%Y%m%d')}.csv"
    return _to_csv_stream(stats_df, filename)
