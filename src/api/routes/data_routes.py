"""Data management API routes for water quality data.

Uses persistent file-based storage via DataManager.
Data survives server restarts.
"""

import math
from datetime import datetime
from pathlib import Path
from typing import Optional


def _safe_json(v: float) -> float | None:
    """Replace NaN/Inf with None for JSON-safe serialization."""
    return None if math.isnan(v) or math.isinf(v) else v

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Query

from src.config import settings
from src.data_manager import data_manager
from src.data_cleaning import DataCleaner
from src.data_collection import CsvCollector, ManualCollector, SensorCollector
from src.models.schemas import (
    CleaningConfig,
    CleaningReportModel,
    UploadResponse,
    WaterQualityRecord,
)

router = APIRouter()


def _df_to_json(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to JSON-serializable list."""
    if df is None or df.empty:
        return []
    result = df.copy()
    if "collection_time" in result.columns:
        result["collection_time"] = result["collection_time"].astype(str)
    return result.replace({float("nan"): None}).to_dict(orient="records")


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV/Excel file containing water quality data."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    upload_dir = Path(settings.raw_data_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    collector = CsvCollector()
    result = collector.collect(str(file_path))

    if not result.success:
        raise HTTPException(
            status_code=422,
            detail={"message": result.message, "errors": result.errors}
        )

    data_manager.raw_data = result.records

    return UploadResponse(
        filename=file.filename,
        records_loaded=result.record_count,
        columns_detected=list(result.records.columns),
        preview=_df_to_json(result.records.head(5)),
    )


@router.post("/upload/simulate")
async def upload_simulated(
    station_id: str = Form("ST001"),
    hours: int = Form(24),
    interval: int = Form(60),
):
    """Generate and load simulated sensor data."""
    collector = SensorCollector()
    result = collector.collect(
        station_id=station_id,
        hours=hours,
        interval_minutes=interval,
    )
    data_manager.raw_data = result.records

    return {
        "message": result.message,
        "records": result.record_count,
        "preview": _df_to_json(result.records.head(5)),
    }


@router.post("/manual")
async def add_manual_record(record: WaterQualityRecord):
    """Add a single manually entered water quality record."""
    collector = ManualCollector()
    result = collector.collect(record.model_dump())

    if not result.success:
        raise HTTPException(
            status_code=422,
            detail={"message": result.message, "errors": result.errors}
        )

    data_manager.append_raw(result.records)

    return {
        "message": "Record added successfully",
        "record": record.model_dump(),
    }


@router.get("/raw")
async def get_raw_data(page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=1000)):
    """Query raw (uncleaned) water quality data with pagination."""
    if not data_manager.has_raw():
        return {"records": [], "total": 0, "page": page, "page_size": page_size}

    df = data_manager.raw_data
    total = len(df)
    start = (page - 1) * page_size
    end = min(start + page_size, total)

    return {
        "records": _df_to_json(df.iloc[start:end]),
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/clean")
async def clean_data(config: CleaningConfig = CleaningConfig()):
    """Execute data cleaning pipeline on raw data."""
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No raw data to clean. Upload data first.")

    cleaner = DataCleaner(config.model_dump())
    cleaned_df, report = cleaner.clean(data_manager.raw_data)

    # Save to disk
    output_dir = Path(settings.cleaned_data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    cleaned_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    data_manager.cleaned_data = cleaned_df

    return CleaningReportModel(
        total_records=report.total_records,
        duplicates_removed=report.duplicates_removed,
        missing_handled=report.missing_handled,
        outliers_removed=report.outliers_removed,
        records_after=report.records_after,
        columns_standardized=report.columns_cleaned,
        summary=report.details.get("summary", ""),
    )


@router.get("/cleaned")
async def get_cleaned_data(page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=1000)):
    """Query cleaned water quality data with pagination."""
    if not data_manager.has_cleaned():
        return {
            "records": [],
            "total": 0,
            "message": "No cleaned data available. Run cleaning first.",
            "page": page,
            "page_size": page_size,
        }

    df = data_manager.cleaned_data
    total = len(df)
    start = (page - 1) * page_size
    end = min(start + page_size, total)

    return {
        "records": _df_to_json(df.iloc[start:end]),
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/summary")
async def get_data_summary():
    """Get statistical summary of currently loaded raw data."""
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No data loaded.")

    df = data_manager.raw_data
    indicators = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]
    summary = {}

    for col in indicators:
        if col in df.columns:
            col_data = df[col].dropna()
            if not col_data.empty:
                summary[col] = {
                    "min": _safe_json(round(float(col_data.min()), 2)),
                    "max": _safe_json(round(float(col_data.max()), 2)),
                    "mean": _safe_json(round(float(col_data.mean()), 2)),
                    "std": _safe_json(round(float(col_data.std()), 2)),
                    "missing": int(df[col].isna().sum()),
                }

    return {
        "station_ids": list(df["station_id"].unique()) if "station_id" in df.columns else [],
        "total_records": len(df),
        "date_range": [
            str(df["collection_time"].min()) if "collection_time" in df.columns else "",
            str(df["collection_time"].max()) if "collection_time" in df.columns else "",
        ],
        "indicators": summary,
    }


@router.delete("/raw")
async def clear_raw_data():
    """Clear all raw data from storage."""
    data_manager.clear_raw()
    return {"message": "Raw data cleared."}


@router.delete("/cleaned")
async def clear_cleaned_data():
    """Clear all cleaned data from storage."""
    data_manager.clear_cleaned()
    return {"message": "Cleaned data cleared."}


@router.get("/info")
async def get_data_info():
    """Get metadata about currently loaded data."""
    return data_manager.get_data_info()


@router.get("/stations")
async def list_stations():
    """List all monitoring stations in the data."""
    return {"stations": data_manager.get_station_list()}
