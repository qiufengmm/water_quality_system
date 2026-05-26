"""Training script for water quality prediction models.

Provides both programmatic and CLI interfaces for training
the XGBoost model on historical water quality data.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import settings
from src.data_cleaning import DataCleaner
from src.ml.xgboost_predictor import XGBoostPredictor

# Default training data path
DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "samples" / "water_quality_sample.csv"


def train_model(data_path: Optional[str] = None,
                target_indicators: Optional[list[str]] = None,
                test_size: float = 0.2,
                save: bool = True) -> XGBoostPredictor:
    """Train water quality prediction model.

    Steps:
    1. Load data from CSV
    2. Clean data (remove outliers, fill missing)
    3. Create features (lags, rolling stats, time features)
    4. Train XGBoost models for each indicator
    5. Evaluate and report metrics
    6. Save model to disk

    Args:
        data_path: Path to training CSV. Uses sample data if None.
        target_indicators: Which indicators to predict.
        test_size: Validation split ratio.
        save: Whether to save the trained model.

    Returns:
        Trained XGBoostPredictor instance.
    """
    # 1. Load data
    path = Path(data_path) if data_path else DEFAULT_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Training data not found: {path}")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading data from {path}")
    df = pd.read_csv(path, parse_dates=["collection_time"], encoding="utf-8-sig")
    print(f"  Loaded {len(df)} records from {len(df['station_id'].unique())} stations")

    # 2. Clean data
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Cleaning data...")
    cleaner = DataCleaner({
        "remove_duplicates": True,
        "handle_missing": "interpolate",
        "outlier_method": "iqr",
        "outlier_threshold": 1.5,
    })
    cleaned_df, report = cleaner.clean(df)
    print(f"  Cleaned: {report.total_records} -> {report.records_after} records "
          f"(removed {report.duplicates_removed} dup + {report.outliers_removed} outliers)")

    # 3. Define targets
    if target_indicators is None:
        target_indicators = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]
    target_indicators = [c for c in target_indicators if c in cleaned_df.columns]
    print(f"  Target indicators: {target_indicators}")

    # 4. Train model
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Training XGBoost models...")
    predictor = XGBoostPredictor()
    metrics = predictor.train(cleaned_df, target_columns=target_indicators, test_size=test_size)

    # 5. Report results
    print(f"\n{'='*50}")
    print(f"Training Results")
    print(f"{'='*50}")
    summary = metrics.get("_summary", {})
    print(f"Indicators: {summary.get('indicators', [])}")
    print(f"Average R^2: {summary.get('avg_r2', 'N/A'):.4f}")
    print(f"Features: {summary.get('features', 0)}")
    print(f"Training records: {summary.get('training_records', 0)}")
    print(f"\nPer-indicator metrics:")
    print(f"{'Indicator':<15} {'R^2':<10} {'MAE':<10} {'RMSE':<10}")
    print(f"{'-'*45}")
    for ind, met in metrics.items():
        if ind == "_summary":
            continue
        print(f"{ind:<15} {met.get('r2', 0):<10.4f} {met.get('mae', 0):<10.4f} {met.get('rmse', 0):<10.4f}")

    # 6. Save model
    if save:
        model_path = predictor.save_model(settings.model_dir)
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Model saved to: {model_path}")

    return predictor


def main():
    """CLI entry point for training."""
    import argparse
    parser = argparse.ArgumentParser(description="Train water quality prediction model")
    parser.add_argument("--data", type=str, help="Path to training data CSV")
    parser.add_argument("--indicators", type=str, nargs="+",
                        default=["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"],
                        help="Indicators to predict")
    parser.add_argument("--test-size", type=float, default=0.2, help="Validation split ratio")
    parser.add_argument("--no-save", action="store_true", help="Don't save model")
    args = parser.parse_args()

    try:
        predictor = train_model(
            data_path=args.data,
            target_indicators=args.indicators,
            test_size=args.test_size,
            save=not args.no_save,
        )
    except Exception as e:
        print(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
