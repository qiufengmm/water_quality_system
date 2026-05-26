"""Feature engineering for water quality prediction models.

Transforms raw water quality time-series data into features suitable
for ML models, including lag features, rolling statistics,
time-based features, and station encoding.
"""

from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd


class FeatureEngineer:
    """Create features from water quality time-series data.

    Generates:
    - Lag features (t-1, t-2, ..., t-n)
    - Rolling window statistics (mean, std, min, max)
    - Time-based features (hour, day, month, weekday)
    - Station one-hot encoding
    - Rate of change (first difference)
    """

    def __init__(self, lag_steps: int = 7, rolling_window: int = 3):
        self.lag_steps = lag_steps
        self.rolling_window = rolling_window
        self.feature_names: list[str] = []
        self._is_fitted = False

    def create_features(self, df: pd.DataFrame,
                        target_cols: Optional[list[str]] = None) -> pd.DataFrame:
        """Create feature matrix from raw time-series data.

        Args:
            df: DataFrame with columns [station_id, collection_time, *indicators].
            target_cols: List of indicator columns to predict.

        Returns:
            DataFrame with engineered features. Target columns are preserved
            for supervised learning.
        """
        if target_cols is None:
            target_cols = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]

        df = df.copy()

        # Ensure sorted by station and time
        if "collection_time" in df.columns:
            df = df.sort_values(["station_id", "collection_time"]).reset_index(drop=True)

        # Remove non-feature columns for processing, keep target cols
        id_cols = ["station_id", "collection_time"]
        indicator_cols = [c for c in target_cols if c in df.columns]

        features = pd.DataFrame(index=df.index)
        features["station_id"] = df["station_id"]

        # 1. Lag features for each indicator
        for col in indicator_cols:
            for lag in range(1, self.lag_steps + 1):
                features[f"{col}_lag_{lag}"] = df.groupby("station_id")[col].shift(lag)

        # 2. Rolling statistics
        for col in indicator_cols:
            features[f"{col}_roll_mean"] = df.groupby("station_id")[col].transform(
                lambda x: x.rolling(window=self.rolling_window, min_periods=1).mean()
            )
            features[f"{col}_roll_std"] = df.groupby("station_id")[col].transform(
                lambda x: x.rolling(window=self.rolling_window, min_periods=1).std()
            ).fillna(0)

        # 3. Rate of change (first difference)
        for col in indicator_cols:
            diff = df.groupby("station_id")[col].diff()
            features[f"{col}_diff"] = diff.fillna(0)

        # 4. Time-based features
        if "collection_time" in df.columns:
            dt = pd.to_datetime(df["collection_time"])
            features["hour"] = dt.dt.hour
            features["day"] = dt.dt.day
            features["month"] = dt.dt.month
            features["dayofweek"] = dt.dt.dayofweek

        # 5. Station encoding (one-hot)
        station_dummies = pd.get_dummies(df["station_id"], prefix="station")
        features = pd.concat([features, station_dummies], axis=1)

        # Drop rows with NaN from lag creation
        features = features.dropna()

        # Store feature names only on first fit (training), not on prediction
        if not self._is_fitted:
            self.feature_names = [c for c in features.columns
                                  if c not in indicator_cols and c != "station_id"]
            self._is_fitted = True

        # Keep target columns for supervised learning
        for col in indicator_cols:
            if col in df.columns:
                # Align target with features (shifted by lag creation dropping)
                features[col] = df.loc[features.index, col]

        return features

    def create_prediction_features(self, recent_df: pd.DataFrame,
                                   target_cols: Optional[list[str]] = None) -> pd.DataFrame:
        """Create features for prediction (no targets needed).

        Uses the most recent window of data to generate features
        for predicting future values.

        Args:
            recent_df: Recent data window for feature generation.
            target_cols: Indicator columns.

        Returns:
            Feature matrix ready for model inference.
        """
        if target_cols is None:
            target_cols = ["ph", "do", "nh3n", "turbidity", "temperature", "cod", "total_phosphorus"]

        features = self.create_features(recent_df, target_cols)

        # Drop target columns for inference
        for col in target_cols:
            if col in features.columns:
                features = features.drop(columns=[col])

        return features
