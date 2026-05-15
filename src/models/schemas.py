"""Pydantic data models for water quality monitoring and prediction system."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WaterGrade(str, Enum):
    """Water quality classification grades."""
    I = "I"       # Excellent
    II = "II"     # Good
    III = "III"   # Moderate
    IV = "IV"     # Poor
    V = "V"       # Bad
    VI = "VI"     # Severely polluted


class WaterQualityRecord(BaseModel):
    """Core water quality data record."""
    station_id: str = Field(..., description="Monitoring station ID")
    collection_time: datetime = Field(..., description="Data collection timestamp")
    ph: Optional[float] = Field(None, ge=0, le=14, description="pH value")
    do: Optional[float] = Field(None, ge=0, description="Dissolved oxygen (mg/L)")
    nh3n: Optional[float] = Field(None, ge=0, description="Ammonia nitrogen (mg/L)")
    turbidity: Optional[float] = Field(None, ge=0, description="Turbidity (NTU)")
    temperature: Optional[float] = Field(None, description="Water temperature (°C)")
    cod: Optional[float] = Field(None, ge=0, description="Chemical oxygen demand (mg/L)")
    total_phosphorus: Optional[float] = Field(None, ge=0, description="Total phosphorus (mg/L)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "station_id": "ST001",
                "collection_time": "2026-05-01T08:00:00",
                "ph": 7.2,
                "do": 6.5,
                "nh3n": 0.15,
                "turbidity": 3.2,
                "temperature": 22.5,
                "cod": 10.0,
                "total_phosphorus": 0.05
            }
        }


class CollectionResult(BaseModel):
    """Result of a data collection operation."""
    success: bool
    record_count: int
    message: str
    errors: list[str] = []


class CleaningConfig(BaseModel):
    """Configuration for data cleaning pipeline."""
    remove_duplicates: bool = True
    handle_missing: str = "interpolate"  # "drop", "interpolate", "fill_mean"
    outlier_method: str = "iqr"          # "iqr", "zscore", "none"
    outlier_threshold: float = 1.5       # IQR multiplier or z-score threshold
    normalize: bool = False
    normalize_method: str = "minmax"     # "minmax", "zscore"


class CleaningReportModel(BaseModel):
    """Report generated after data cleaning."""
    total_records: int
    duplicates_removed: int
    missing_handled: int
    outliers_removed: int
    records_after: int
    columns_standardized: list[str]
    summary: str


class DataSummary(BaseModel):
    """Statistical summary of water quality data."""
    station_id: str
    record_count: int
    date_range: tuple[str, str]
    ph: Optional[dict] = None
    do: Optional[dict] = None
    nh3n: Optional[dict] = None
    turbidity: Optional[dict] = None
    temperature: Optional[dict] = None
    cod: Optional[dict] = None
    total_phosphorus: Optional[dict] = None


class UploadResponse(BaseModel):
    """Response for file upload operations."""
    filename: str
    records_loaded: int
    columns_detected: list[str]
    preview: list[dict]
