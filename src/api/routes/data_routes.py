"""Data management API routes for water quality data."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.config import settings
from src.data_cleaning import DataCleaner, CleaningReport
from src.data_collection import CsvCollector, ManualCollector, SensorCollector
from src.models.schemas import (
    CleaningConfig,
    CleaningReportModel,
    DataSummary,
    UploadResponse,
    WaterQualityRecord,
)

router = APIRouter()

# In-memory storage (Week 1: file-based, Week 3+: migrate to MySQL)
_raw_data: Optional[pd.DataFrame] = None
_cleaned_data: Optional[pd.DataFrame] = None


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
    global _raw_data

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Save uploaded file
    upload_dir = Path(settings.raw_data_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Import data
    collector = CsvCollector()
    result = collector.collect(str(file_path))

    if not result.success:
        raise HTTPException(
            status_code=422,
            detail={"message": result.message, "errors": result.errors}
        )

    _raw_data = result.records

    preview = _df_to_json(result.records.head(5))
    columns = list(result.records.columns)

    return UploadResponse(
        filename=file.filename,
        records_loaded=result.record_count,
        columns_detected=columns,
        preview=preview,
    )


@router.post("/upload/simulate")
async def upload_simulated(
    station_id: str = Form("ST001"),
    hours: int = Form(24),
    interval: int = Form(60),
):
    """Generate and load simulated sensor data."""
    global _raw_data

    collector = SensorCollector()
    result = collector.collect(
        station_id=station_id,
        hours=hours,
        interval_minutes=interval,
    )

    _raw_data = result.records

    return {
        "message": result.message,
        "records": result.record_count,
        "preview": _df_to_json(result.records.head(5)),
    }


@router.post("/manual")
async def add_manual_record(record: WaterQualityRecord):
    """Add a single manually entered water quality record."""
    global _raw_data

    collector = ManualCollector()
    result = collector.collect(record.model_dump())

    if not result.success:
        raise HTTPException(
            status_code=422,
            detail={"message": result.message, "errors": result.errors}
        )

    # Append to existing raw data
    if _raw_data is not None and not _raw_data.empty:
        _raw_data = pd.concat([_raw_data, result.records], ignore_index=True)
    else:
        _raw_data = result.records

    return {
        "message": "Record added successfully",
        "record": record.model_dump(),
    }


@router.get("/raw")
async def get_raw_data(page: int = 1, page_size: int = 100):
    """Query raw (uncleaned) water quality data with pagination."""
    global _raw_data

    if _raw_data is None or _raw_data.empty:
        return {"records": [], "total": 0, "page": page, "page_size": page_size}

    total = len(_raw_data)
    start = (page - 1) * page_size
    end = min(start + page_size, total)

    return {
        "records": _df_to_json(_raw_data.iloc[start:end]),
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/clean")
async def clean_data(config: CleaningConfig = CleaningConfig()):
    """Execute data cleaning pipeline on raw data."""
    global _raw_data, _cleaned_data

    if _raw_data is None or _raw_data.empty:
        raise HTTPException(status_code=400, detail="No raw data to clean. Upload data first.")

    cleaner = DataCleaner(config.model_dump())
    cleaned_df, report = cleaner.clean(_raw_data)

    # Save cleaned data
    output_dir = Path(settings.cleaned_data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    cleaned_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    _cleaned_data = cleaned_df

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
async def get_cleaned_data(page: int = 1, page_size: int = 100):
    """Query cleaned water quality data with pagination."""
    global _cleaned_data

    if _cleaned_data is None or _cleaned_data.empty:
        return {
            "records": [],
            "total": 0,
            "message": "No cleaned data available. Run cleaning first.",
            "page": page,
            "page_size": page_size,
        }

    total = len(_cleaned_data)
    start = (page - 1) * page_size
    end = min(start + page_size, total)

    return {
        "records": _df_to_json(_cleaned_data.iloc[start:end]),
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/summary")
async def get_data_summary():
    """Get statistical summary of currently loaded raw data."""
    global _raw_data

    if _raw_data is None or _raw_data.empty:
        raise HTTPException(status_code=400, detail="No data loaded.")

    indicators = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]
    summary = {}

    for col in indicators:
        if col in _raw_data.columns:
            col_data = _raw_data[col].dropna()
            if not col_data.empty:
                summary[col] = {
                    "min": round(float(col_data.min()), 2),
                    "max": round(float(col_data.max()), 2),
                    "mean": round(float(col_data.mean()), 2),
                    "std": round(float(col_data.std()), 2),
                    "missing": int(_raw_data[col].isna().sum()),
                }

    return {
        "station_ids": list(_raw_data["station_id"].unique()) if "station_id" in _raw_data.columns else [],
        "total_records": len(_raw_data),
        "date_range": [
            str(_raw_data["collection_time"].min()) if "collection_time" in _raw_data.columns else "",
            str(_raw_data["collection_time"].max()) if "collection_time" in _raw_data.columns else "",
        ],
        "indicators": summary,
    }
