"""Prediction API routes for water quality forecasting."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from src.config import settings
from src.data_cleaning import DataCleaner
from src.data_manager import data_manager
from src.ml import XGBoostPredictor
from src.ml.train import train_model

router = APIRouter()

# Global predictor instance (lazy-loaded)
_predictor: Optional[XGBoostPredictor] = None


def _get_predictor() -> XGBoostPredictor:
    """Get or initialize the predictor."""
    global _predictor

    # Try loading existing model first
    model_dir = Path(settings.model_dir)
    if _predictor is None and model_dir.exists():
        # Find most recent model directory
        xgb_dirs = sorted(model_dir.glob("xgboost_*"))
        if xgb_dirs:
            _predictor = XGBoostPredictor()
            if _predictor.load_model(str(xgb_dirs[-1])):
                return _predictor

    # If still None, need to train
    if _predictor is None or not _predictor.is_trained:
        raise HTTPException(
            status_code=400,
            detail="No trained model available. Train first via POST /api/predict/train"
        )

    return _predictor


@router.post("/predict/train")
async def train_prediction_model():
    """Train XGBoost prediction model on loaded data."""
    global _predictor

    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No raw data loaded. Upload data first.")

    try:
        _predictor = train_model(
            data_path=None,  # Use sample data as base
            save=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

    info = _predictor.get_model_info()
    return {
        "message": "Model trained successfully",
        "indicators": info["target_indicators"],
        "metrics": info["metrics"],
        "avg_r2": info["metrics"].get("_summary", {}).get("avg_r2"),
        "model_path": _predictor.save_model(settings.model_dir),
    }


@router.post("/predict/train/from-data")
async def train_from_loaded_data():
    """Train model using currently loaded raw data."""
    global _predictor

    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No raw data loaded.")

    df = data_manager.raw_data
    if len(df) < 20:
        raise HTTPException(status_code=400, detail=f"Need at least 20 records, got {len(df)}")

    # Clean data before training
    cleaner = DataCleaner({
        "remove_duplicates": True,
        "handle_missing": "interpolate",
        "outlier_method": "iqr",
        "outlier_threshold": 1.5,
    })
    cleaned_df, _ = cleaner.clean(df)

    _predictor = XGBoostPredictor()
    metrics = _predictor.train(cleaned_df)

    # Save model
    _predictor.save_model(settings.model_dir)

    summary = metrics.get("_summary", {})
    return {
        "message": "Model trained on loaded data",
        "records_used": summary.get("training_records", len(df)),
        "avg_r2": summary.get("avg_r2"),
        "metrics": {k: v for k, v in metrics.items() if k != "_summary"},
    }


@router.post("/predict/batch")
async def predict_batch(
    station_id: str = Query("ST001", description="Station to predict for"),
    days: int = Query(7, ge=1, le=30, description="Prediction horizon in days"),
):
    """Predict water quality indicators for a station."""
    predictor = _get_predictor()

    # Get recent data for this station
    if not data_manager.has_raw():
        raise HTTPException(status_code=400, detail="No data loaded.")

    df = data_manager.raw_data
    station_df = df[df["station_id"] == station_id].copy()

    if station_df.empty:
        # Fall back to sample data
        sample_path = Path(settings.sample_data_dir) / "water_quality_sample.csv"
        if sample_path.exists():
            station_df = pd.read_csv(sample_path, parse_dates=["collection_time"], encoding="utf-8-sig")
            station_df = station_df[station_df["station_id"] == station_id]

    if station_df.empty:
        raise HTTPException(status_code=404, detail=f"No data for station {station_id}")

    result = predictor.predict(station_df, days=days)

    if not result.success:
        raise HTTPException(status_code=422, detail=result.message)

    return {
        "station_id": result.station_id,
        "prediction_dates": result.dates,
        "predictions": result.predictions,
        "confidence": result.confidence,
        "message": result.message,
    }


@router.get("/predict/model-info")
async def get_model_info():
    """Get information about the current prediction model."""
    try:
        predictor = _get_predictor()
        return predictor.get_model_info()
    except HTTPException:
        return {
            "status": "not_ready",
            "message": "No trained model available. POST /api/predict/train to train one."
        }


@router.get("/predict/history")
async def get_prediction_history():
    """List available saved models."""
    model_dir = Path(settings.model_dir)
    if not model_dir.exists():
        return {"models": []}

    xgb_dirs = sorted(model_dir.glob("xgboost_*"), reverse=True)
    models = []
    for d in xgb_dirs:
        meta_path = d / "metadata.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            models.append({
                "path": str(d),
                "timestamp": meta.get("timestamp", ""),
                "indicators": meta.get("target_indicators", []),
                "avg_r2": round(
                    np.mean([m.get("r2", 0) for m in meta.get("metrics", {}).values() if isinstance(m, dict)]), 4
                ) if meta.get("metrics") else None,
            })

    return {"models": models}
