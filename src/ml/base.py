"""Abstract base class for water quality prediction models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pandas as pd


@dataclass
class PredictionResult:
    """Standard result from a prediction operation."""
    success: bool
    station_id: str
    predictions: dict[str, list[float]] = field(default_factory=dict)
    dates: list[str] = field(default_factory=list)
    confidence: float = 0.0
    message: str = ""
    errors: list[str] = field(default_factory=list)


class AbstractPredictor(ABC):
    """Abstract base class for all water quality predictors.

    All prediction model implementations must inherit from this class
    and implement the train(), predict(), save_model(), and load_model() methods.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_trained = False
        self.feature_columns: list[str] = []
        self.target_columns: list[str] = []

    @abstractmethod
    def train(self, df: pd.DataFrame, target_columns: Optional[list[str]] = None, **kwargs) -> dict:
        """Train the prediction model on historical data.

        Args:
            df: Training data with features and targets.
            target_columns: Columns to predict.

        Returns:
            Training metrics dictionary.
        """
        pass

    @abstractmethod
    def predict(self, df: pd.DataFrame, days: int = 7) -> PredictionResult:
        """Generate predictions for future time points.

        Args:
            df: Input features for prediction.
            days: Number of days to predict ahead.

        Returns:
            PredictionResult with forecasted values.
        """
        pass

    @abstractmethod
    def save_model(self, path: str) -> str:
        """Save trained model to disk.

        Args:
            path: Directory to save model to.

        Returns:
            Full path to saved model file.
        """
        pass

    @abstractmethod
    def load_model(self, path: str) -> bool:
        """Load trained model from disk.

        Args:
            path: Path to model file.

        Returns:
            True if loaded successfully.
        """
        pass

    def get_feature_importance(self) -> Optional[dict]:
        """Get feature importance scores if available."""
        return None
