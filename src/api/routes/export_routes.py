"""Data export API routes.

Provides CSV, JSON, and Excel export of raw and cleaned data.
Also generates comprehensive statistical reports in Excel format.
"""

from datetime import datetime
from io import BytesIO, StringIO
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


# ── Excel Export ────────────────────────────────────────

def _to_excel_response(df: pd.DataFrame, filename: str, sheet_name: str = "Sheet1") -> StreamingResponse:
    """Convert DataFrame to Excel streaming response using openpyxl."""
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/raw/excel")
async def export_raw_excel():
    """Export raw data as Excel (.xlsx) file download."""
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No raw data available.")
    filename = f"raw_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return _to_excel_response(data_manager.raw_data, filename, "原始数据")


@router.get("/cleaned/excel")
async def export_cleaned_excel():
    """Export cleaned data as Excel (.xlsx) file download."""
    if not data_manager.has_cleaned():
        raise HTTPException(status_code=400, detail="No cleaned data available.")
    filename = f"cleaned_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return _to_excel_response(data_manager.cleaned_data, filename, "清洗数据")


@router.get("/report")
async def export_full_report():
    """Generate a comprehensive Excel report with multiple sheets."""
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No data loaded.")

    buf = BytesIO()
    indicators = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Sheet 1: Raw data
        if data_manager.has_raw():
            data_manager.raw_data.to_excel(writer, index=False, sheet_name="原始数据")

        # Sheet 2: Cleaned data
        if data_manager.has_cleaned():
            data_manager.cleaned_data.to_excel(writer, index=False, sheet_name="清洗数据")

        # Sheet 3: Statistical summary
        df = data_manager.raw_data
        stats_rows = []
        for col in indicators:
            if col in df.columns:
                col_data = df[col].dropna()
                if not col_data.empty:
                    stats_rows.append({
                        "指标": col,
                        "记录数": int(col_data.count()),
                        "最小值": round(float(col_data.min()), 4),
                        "最大值": round(float(col_data.max()), 4),
                        "均值": round(float(col_data.mean()), 4),
                        "标准差": round(float(col_data.std()), 4),
                        "缺失数": int(df[col].isna().sum()),
                    })
        stats_df = pd.DataFrame(stats_rows)
        stats_df.to_excel(writer, index=False, sheet_name="统计摘要")

        # Sheet 4: Data info
        info = data_manager.get_data_info()
        info_rows = [
            {"项目": "总记录数", "值": info.get("raw_records", 0)},
            {"项目": "站点数", "值": len(info.get("stations", []))},
            {"项目": "站点列表", "值": ", ".join(info.get("stations", []))},
            {"项目": "清洗后记录", "值": info.get("cleaned_records", 0)},
        ]
        if info.get("raw_date_range"):
            info_rows.append({"项目": "数据时间范围", "值": f"{info['raw_date_range'][0]} ~ {info['raw_date_range'][1]}"})
        info_df = pd.DataFrame(info_rows)
        info_df.to_excel(writer, index=False, sheet_name="数据信息")

    buf.seek(0)
    filename = f"full_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
