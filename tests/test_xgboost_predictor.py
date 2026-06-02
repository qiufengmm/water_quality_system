"""Unit tests for XGBoost predictor module."""

from pathlib import Path

import pandas as pd
import pytest

from src.ml.base import AbstractPredictor, PredictionResult
from src.ml.xgboost_predictor import XGBoostPredictor


class TestPredictionResult:
    """Tests for PredictionResult dataclass."""

    def test_default_values(self):
        """Default values for optional fields."""
        r = PredictionResult(success=False, station_id="")
        assert r.success is False
        assert r.station_id == ""
        assert r.predictions == {}
        assert r.dates == []
        assert r.confidence == 0.0
        assert r.message == ""
        assert r.errors == []

    def test_custom_values(self):
        """All fields settable via constructor."""
        r = PredictionResult(
            success=True,
            station_id="ST001",
            predictions={"ph": [7.0, 7.1]},
            dates=["2026-05-01", "2026-05-02"],
            confidence=0.95,
            message="OK",
            errors=[],
        )
        assert r.success is True
        assert r.station_id == "ST001"
        assert len(r.predictions["ph"]) == 2


class TestAbstractPredictor:
    """Tests for AbstractPredictor base class."""

    def test_cannot_instantiate(self):
        """AbstractPredictor() raises TypeError."""
        with pytest.raises(TypeError):
            AbstractPredictor("test")

    def test_concrete_subclass_works(self):
        """A minimal subclass can be instantiated."""
        class MinimalPredictor(AbstractPredictor):
            def train(self, df, target_columns=None, **kwargs):
                return {}
            def predict(self, df, days=7):
                return PredictionResult(success=False, station_id="")
            def save_model(self, path):
                return ""
            def load_model(self, path):
                return False

        p = MinimalPredictor("test")
        assert p.model_name == "test"
        assert p.is_trained is False


class TestXGBoostPredictorInit:
    """Tests for XGBoostPredictor initialization."""

    def test_model_name(self):
        """model_name is 'xgboost'."""
        p = XGBoostPredictor()
        assert p.model_name == "xgboost"

    def test_default_params(self):
        """DEFAULT_PARAMS merged into self.params."""
        p = XGBoostPredictor()
        assert p.params["n_estimators"] == 200
        assert p.params["max_depth"] == 6
        assert p.params["learning_rate"] == 0.08

    def test_custom_params_override(self):
        """Custom params override specific defaults."""
        p = XGBoostPredictor(params={"n_estimators": 100, "max_depth": 4})
        assert p.params["n_estimators"] == 100
        assert p.params["max_depth"] == 4
        # Unchanged defaults preserved
        assert p.params["learning_rate"] == 0.08

    def test_not_trained_initially(self):
        """is_trained is False."""
        p = XGBoostPredictor()
        assert p.is_trained is False

    def test_no_models_initially(self):
        """models dict is empty."""
        p = XGBoostPredictor()
        assert p.models == {}


class TestXGBoostPredictorTrain:
    """Tests for training."""

    def test_train_returns_metrics_dict(self, sample_training_df):
        """Train returns dict with per-indicator metrics."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        result = p.train(sample_training_df, ["ph", "do"])
        assert isinstance(result, dict)
        assert "ph" in result
        assert "do" in result

    def test_train_all_indicators(self, sample_training_df):
        """All 7 default indicators have metrics."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        result = p.train(sample_training_df)
        for ind in ("ph", "do", "nh3n", "cod", "turbidity", "temperature"):
            assert ind in result, f"Missing indicator: {ind}"

    def test_train_sets_is_trained(self, sample_training_df):
        """is_trained becomes True."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph"])
        assert p.is_trained is True

    def test_train_metrics_have_required_keys(self, sample_training_df):
        """Metrics dict has r2, mae, rmse."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        result = p.train(sample_training_df, ["ph"])
        for key in ("r2", "mae", "rmse"):
            assert key in result["ph"], f"Missing metric: {key}"

    def test_train_insufficient_data(self, sample_df):
        """Very small data returns error dict."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        result = p.train(sample_df, ["ph"])
        assert "error" in result

    def test_train_has_summary(self, sample_training_df):
        """Result has _summary with avg_r2."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        result = p.train(sample_training_df, ["ph"])
        assert "_summary" in result
        assert "avg_r2" in result["_summary"]


class TestXGBoostPredictorPredict:
    """Tests for prediction."""

    def test_predict_not_trained(self, sample_df):
        """Not trained returns error PredictionResult."""
        p = XGBoostPredictor()
        result = p.predict(sample_df)
        assert result.success is False
        assert "not trained" in result.message.lower()

    def test_predict_after_train(self, sample_training_df):
        """Train then predict returns success."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph", "do"])
        result = p.predict(sample_training_df, days=3)
        assert result.success is True

    def test_predict_returns_correct_structure(self, sample_training_df):
        """PredictionResult has predictions dict and dates."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph", "do"])
        result = p.predict(sample_training_df, days=3)
        assert isinstance(result.predictions, dict)
        assert "ph" in result.predictions
        assert "do" in result.predictions
        assert len(result.dates) == 3

    def test_predict_days_param(self, sample_training_df):
        """Number of predicted dates equals days param."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph"])
        for days in (1, 3, 7):
            result = p.predict(sample_training_df, days=days)
            assert len(result.dates) == days, f"Failed for days={days}"
            assert len(result.predictions["ph"]) == days

    def test_predict_insufficient_data(self, sample_df, sample_training_df):
        """Too few rows returns error."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph"])
        # sample_df has only 10 rows; need lag_steps+1 = 8, so 10 > 8, should work
        # Use even fewer rows
        tiny = sample_df.iloc[:3]
        result = p.predict(tiny, days=3)
        assert result.success is False


class TestXGBoostPredictorSaveLoad:
    """Tests for model persistence."""

    def test_save_model_creates_directory(self, sample_training_df, tmp_path):
        """Save creates model directory."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph"])
        saved_path = p.save_model(str(tmp_path))
        assert Path(saved_path).exists()

    def test_save_model_contains_files(self, sample_training_df, tmp_path):
        """Saved model directory contains expected files."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph"])
        saved_path = Path(p.save_model(str(tmp_path)))
        assert (saved_path / "metadata.json").exists()
        assert (saved_path / "feature_config.pkl").exists()
        assert (saved_path / "ph.json").exists()

    def test_load_model(self, sample_training_df, tmp_path):
        """Loaded model has same target_indicators."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph", "do"])
        saved_path = p.save_model(str(tmp_path))

        p2 = XGBoostPredictor()
        result = p2.load_model(saved_path)
        assert result is True
        assert p2.is_trained is True
        assert p2.target_indicators == ["ph", "do"]

    def test_load_model_nonexistent_path(self):
        """Returns False for invalid path."""
        p = XGBoostPredictor()
        result = p.load_model("/nonexistent/path")
        assert result is False


class TestXGBoostPredictorInfo:
    """Tests for model info methods."""

    def test_get_feature_importance_not_trained(self):
        """Returns None when no models."""
        p = XGBoostPredictor()
        assert p.get_feature_importance() is None

    def test_get_feature_importance_after_train(self, sample_training_df):
        """Returns dict with feature names."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph"])
        importance = p.get_feature_importance()
        assert importance is not None
        assert len(importance) > 0

    def test_get_model_info(self, sample_training_df):
        """Model info contains expected keys."""
        p = XGBoostPredictor(params={"n_estimators": 20, "max_depth": 3, "verbosity": 0})
        p.train(sample_training_df, ["ph"])
        info = p.get_model_info()
        assert info["model_name"] == "xgboost"
        assert info["is_trained"] is True
        assert "target_indicators" in info
        assert "num_features" in info
        assert "params" in info
        assert "metrics" in info

    def test_get_model_info_not_trained(self):
        """Model info when not trained shows is_trained=False."""
        p = XGBoostPredictor()
        info = p.get_model_info()
        assert info["is_trained"] is False
        assert info["target_indicators"] == []
