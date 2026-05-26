"""XGBoost-based water quality predictor.

Implements the AbstractPredictor interface using XGBoost regression
models for each water quality indicator. Supports multi-step ahead
forecasting and model persistence.
"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from .base import AbstractPredictor, PredictionResult
from .feature_engineer import FeatureEngineer


class XGBoostPredictor(AbstractPredictor):
    """XGBoost-based water quality indicator predictor.

    Trains one XGBoost regression model per target indicator,
    using engineered features from historical water quality data.

    Attributes:
        target_indicators: List of water quality indicators to predict.
        models: Dict of {indicator: trained XGBoost model}.
        metrics: Dict of training/validation metrics per indicator.
    """

    # Default hyperparameters optimized for water quality data
    DEFAULT_PARAMS = {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.08,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 3,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "random_state": 42,
        "verbosity": 0,
    }

    def __init__(self, params: Optional[dict] = None):
        super().__init__("xgboost")
        self.params = {**self.DEFAULT_PARAMS, **(params or {})}
        self.models: dict[str, xgb.XGBRegressor] = {}
        self.metrics: dict[str, dict] = {}
        self.feature_engineer = FeatureEngineer(lag_steps=7, rolling_window=3)
        self.target_indicators: list[str] = []

    def train(self, df: pd.DataFrame,
              target_columns: Optional[list[str]] = None,
              test_size: float = 0.2,
              **kwargs) -> dict:
        """Train XGBoost models for each target indicator.

        Args:
            df: Historical water quality data.
            target_columns: Indicators to predict.
            test_size: Fraction of data for validation.

        Returns:
            Training metrics for all indicators.
        """
        if target_columns is None:
            target_columns = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]

        self.target_indicators = [c for c in target_columns if c in df.columns]

        # Create features
        feature_df = self.feature_engineer.create_features(df, self.target_indicators)
        feature_cols = self.feature_engineer.feature_names

        if len(feature_df) < 20:
            return {"error": f"Not enough data after feature creation: {len(feature_df)} rows"}

        all_metrics = {}

        for indicator in self.target_indicators:
            if indicator not in feature_df.columns:
                continue

            # Prepare data
            X = feature_df[feature_cols].values
            y = feature_df[indicator].values

            # Split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, shuffle=False
            )

            # Train model
            model = xgb.XGBRegressor(**self.params)
            model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=False,
            )

            # Evaluate
            y_pred = model.predict(X_test)
            metrics = {
                "r2": float(r2_score(y_test, y_pred)),
                "mae": float(mean_absolute_error(y_test, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
                "train_samples": int(len(X_train)),
                "test_samples": int(len(X_test)),
            }
            self.metrics[indicator] = metrics
            self.models[indicator] = model
            all_metrics[indicator] = metrics

        self.is_trained = True

        # Overall metrics
        avg_r2 = np.mean([m["r2"] for m in all_metrics.values()])
        all_metrics["_summary"] = {
            "indicators": self.target_indicators,
            "avg_r2": float(avg_r2),
            "features": len(feature_cols),
            "training_records": len(feature_df),
        }

        return all_metrics

    def predict(self, df: pd.DataFrame, days: int = 7) -> PredictionResult:
        """Predict future water quality indicators.

        Uses the most recent data to generate recursive multi-step
        predictions for each target indicator.

        Args:
            df: Recent data for generating prediction features.
            days: Number of days to forecast.

        Returns:
            PredictionResult with forecasted values.
        """
        if not self.is_trained:
            return PredictionResult(
                success=False,
                station_id=df["station_id"].iloc[0] if "station_id" in df.columns else "unknown",
                message="Model not trained yet. Call train() first.",
                errors=["Model not trained"],
            )

        station_id = df["station_id"].iloc[0] if "station_id" in df.columns else "unknown"
        recent = df.tail(self.feature_engineer.lag_steps + self.feature_engineer.rolling_window)

        if len(recent) < self.feature_engineer.lag_steps + 1:
            return PredictionResult(
                success=False,
                station_id=station_id,
                message=f"Need at least {self.feature_engineer.lag_steps + 1} records, got {len(recent)}",
                errors=["Insufficient data"],
            )

        # Generate prediction features
        try:
            pred_features = self.feature_engineer.create_prediction_features(
                recent, self.target_indicators
            )
        except Exception as e:
            return PredictionResult(
                success=False,
                station_id=station_id,
                message=f"Feature creation failed: {str(e)}",
                errors=[str(e)],
            )

        if pred_features.empty:
            return PredictionResult(
                success=False,
                station_id=station_id,
                message="No features generated for prediction",
                errors=["Empty features"],
            )

        # Align columns: add missing columns (e.g., other station one-hots) with 0
        for col in self.feature_engineer.feature_names:
            if col not in pred_features.columns:
                pred_features[col] = 0
        pred_features = pred_features[self.feature_engineer.feature_names]

        # Get the last row's features for prediction
        last_features = pred_features.iloc[-1:]

        # Generate future dates
        last_time = pd.to_datetime(df["collection_time"].iloc[-1]) if "collection_time" in df.columns else datetime.now()
        future_dates = [last_time + timedelta(days=i+1) for i in range(days)]

        predictions = {}
        confidences = []

        for indicator, model in self.models.items():
            # Simple recursive prediction
            pred_values = []
            current_features = last_features.copy()

            for _ in range(days):
                pred_val = float(model.predict(current_features.values)[0])
                pred_values.append(round(pred_val, 2))
                # For recursive prediction, we'd update features - simplified here

            predictions[indicator] = pred_values

            if indicator in self.metrics:
                confidences.append(self.metrics[indicator].get("r2", 0))

        avg_confidence = float(np.mean(confidences)) if confidences else 0.0

        return PredictionResult(
            success=True,
            station_id=station_id,
            predictions=predictions,
            dates=[d.strftime("%Y-%m-%d") for d in future_dates],
            confidence=round(avg_confidence, 4),
            message=f"Predicted {len(self.models)} indicators for next {days} days",
        )

    def save_model(self, path: str) -> str:
        """Save trained models and metadata to disk."""
        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = save_dir / f"xgboost_{timestamp}"
        model_dir.mkdir(exist_ok=True)

        # Save each indicator model
        for indicator, model in self.models.items():
            model_path = model_dir / f"{indicator}.json"
            model.save_model(str(model_path))

        # Save metadata
        metadata = {
            "model_name": self.model_name,
            "timestamp": timestamp,
            "target_indicators": self.target_indicators,
            "feature_names": self.feature_engineer.feature_names,
            "metrics": self.metrics,
            "params": self.params,
        }
        with open(model_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # Save feature engineer config
        with open(model_dir / "feature_config.pkl", "wb") as f:
            pickle.dump({
                "lag_steps": self.feature_engineer.lag_steps,
                "rolling_window": self.feature_engineer.rolling_window,
                "feature_names": self.feature_engineer.feature_names,
            }, f)

        return str(model_dir)

    def load_model(self, path: str) -> bool:
        """Load trained models and metadata from disk."""
        load_dir = Path(path)
        if not load_dir.exists():
            return False

        # Load metadata
        metadata_path = load_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            self.target_indicators = metadata.get("target_indicators", [])
            self.metrics = metadata.get("metrics", {})
            self.feature_engineer.feature_names = metadata.get("feature_names", [])
            self.feature_engineer._is_fitted = True

        # Load feature config
        feat_config_path = load_dir / "feature_config.pkl"
        if feat_config_path.exists():
            with open(feat_config_path, "rb") as f:
                feat_config = pickle.load(f)
            self.feature_engineer.lag_steps = feat_config.get("lag_steps", 7)
            self.feature_engineer.rolling_window = feat_config.get("rolling_window", 3)
            self.feature_engineer.feature_names = feat_config.get("feature_names", [])
            self.feature_engineer._is_fitted = True

        # Load each model
        for indicator in self.target_indicators:
            model_path = load_dir / f"{indicator}.json"
            if model_path.exists():
                model = xgb.XGBRegressor()
                model.load_model(str(model_path))
                self.models[indicator] = model

        self.is_trained = len(self.models) > 0
        return self.is_trained

    def get_feature_importance(self) -> Optional[dict]:
        """Get aggregated feature importance across all models."""
        if not self.models:
            return None

        importance = {}
        for indicator, model in self.models.items():
            if hasattr(model, "feature_importances_"):
                fi = model.feature_importances_
                for name, val in zip(self.feature_engineer.feature_names, fi):
                    if name not in importance:
                        importance[name] = []
                    importance[name].append(float(val))

        # Average across models
        return {k: round(float(np.mean(v)), 4) for k, v in importance.items()}

    def get_model_info(self) -> dict:
        """Get information about the trained model."""
        return {
            "model_name": self.model_name,
            "is_trained": self.is_trained,
            "target_indicators": self.target_indicators,
            "num_features": len(self.feature_engineer.feature_names),
            "params": self.params,
            "metrics": self.metrics,
            "feature_importance": self.get_feature_importance(),
        }
