"""ML module for water quality prediction.

Provides feature engineering, model training, and prediction capabilities
using XGBoost and other ML algorithms.
"""

from .base import AbstractPredictor, PredictionResult
from .xgboost_predictor import XGBoostPredictor
from .feature_engineer import FeatureEngineer

__all__ = ["AbstractPredictor", "PredictionResult", "XGBoostPredictor", "FeatureEngineer"]
