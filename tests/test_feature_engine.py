"""Unit tests for the feature engineering module."""

import pandas as pd
import pytest

from src.ml.feature_engineer import FeatureEngineer


class TestFeatureEngineerInit:
    """Tests for FeatureEngineer initialization."""

    def test_default_params(self):
        """Default lag_steps=7, rolling_window=3."""
        fe = FeatureEngineer()
        assert fe.lag_steps == 7
        assert fe.rolling_window == 3

    def test_custom_params(self):
        """Constructor accepts custom params."""
        fe = FeatureEngineer(lag_steps=3, rolling_window=2)
        assert fe.lag_steps == 3
        assert fe.rolling_window == 2

    def test_not_fitted_initially(self):
        """_is_fitted is False, feature_names is empty."""
        fe = FeatureEngineer()
        assert fe._is_fitted is False
        assert fe.feature_names == []


class TestFeatureEngineerCreateFeatures:
    """Tests for create_features method."""

    def test_returns_dataframe(self, sample_df):
        """Return type is pd.DataFrame."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_lag_features_created(self, sample_df):
        """Lag columns like ph_lag_1, ph_lag_2 exist."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df, ["ph", "do"])
        for col in ("ph_lag_1", "ph_lag_2", "do_lag_1", "do_lag_2"):
            assert col in result.columns

    def test_rolling_stats_created(self, sample_df):
        """Rolling mean/std columns exist."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df, ["ph"])
        assert "ph_roll_mean" in result.columns
        assert "ph_roll_std" in result.columns

    def test_rate_of_change_created(self, sample_df):
        """Diff column exists."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df, ["ph"])
        assert "ph_diff" in result.columns

    def test_time_features_created(self, sample_df):
        """Time-based columns exist."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df, ["ph"])
        for col in ("hour", "day", "month", "dayofweek"):
            assert col in result.columns

    def test_station_one_hot_created(self, sample_df):
        """Station one-hot columns exist."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df, ["ph"])
        assert "station_ST001" in result.columns
        assert "station_ST002" in result.columns

    def test_target_cols_preserved(self, sample_df):
        """Target columns still present in output."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df, ["ph", "do"])
        assert "ph" in result.columns
        assert "do" in result.columns

    def test_nan_rows_dropped(self, sample_df):
        """First lag_steps rows per station dropped due to NaN from lag."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df, ["ph"])
        # 10 rows - 2 (lag) * 2 (stations) = 6 rows (due to per-group shift)
        # Actually: each station has 5 rows. With lag=2, first 2 rows per station are NaN.
        # So we lose 2 rows per station = 4 NaN rows dropped, leaving 6 rows.
        assert len(result) == 6

    def test_station_id_not_in_features(self, sample_df):
        """station_id column excluded from feature_names."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        fe.create_features(sample_df, ["ph"])
        assert "station_id" not in fe.feature_names

    def test_feature_names_frozen(self, sample_df):
        """feature_names is set after first fit."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        fe.create_features(sample_df, ["ph"])
        assert fe._is_fitted is True
        assert len(fe.feature_names) > 0


class TestFeatureEngineerPredictionFeatures:
    """Tests for create_prediction_features method."""

    def test_target_cols_dropped(self, sample_df):
        """Target columns removed from output."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_prediction_features(sample_df, ["ph", "do"])
        assert "ph" not in result.columns
        assert "do" not in result.columns

    def test_feature_columns_present(self, sample_df):
        """All feature columns exist in prediction features."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_prediction_features(sample_df, ["ph"])
        # After create_features, fe.feature_names is frozen
        for col in fe.feature_names:
            assert col in result.columns, f"Missing feature column: {col}"


class TestFeatureEngineerEdgeCases:
    """Tests for edge cases."""

    def test_single_station(self):
        """Works with one station."""
        df = pd.DataFrame({
            "station_id": ["ST001"] * 10,
            "collection_time": pd.date_range("2026-05-01", periods=10, freq="D"),
            "ph": [7.0 + i * 0.1 for i in range(10)],
            "do": [6.0] * 10,
        })
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(df, ["ph", "do"])
        assert len(result) > 0
        assert "station_ST001" in result.columns

    def test_missing_indicator_columns(self, sample_df):
        """Missing indicators are silently skipped."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df, ["nonexistent_indicator"])
        # No error, result has no NaN since no lag features created for missing
        # Actually the result will have time features and station one-hot
        assert isinstance(result, pd.DataFrame)

    def test_target_cols_none_defaults(self, sample_df):
        """Default target_cols includes all 7 indicators."""
        fe = FeatureEngineer(lag_steps=2, rolling_window=2)
        result = fe.create_features(sample_df)  # No target_cols specified
        assert "ph" in result.columns
        assert "do" in result.columns
