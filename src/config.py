"""System-wide configuration management."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or config file."""

    # Application
    app_name: str = "Water Quality Monitoring & Prediction System"
    app_version: str = "1.0.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Data paths
    data_dir: str = str(Path(__file__).parent.parent / "data")
    raw_data_dir: str = ""
    cleaned_data_dir: str = ""
    sample_data_dir: str = ""

    # Model
    model_dir: str = ""
    default_prediction_days: int = 7

    # Alert thresholds (based on Chinese Surface Water Quality Standards GB 3838-2002)
    alert_ph_min: float = 6.0
    alert_ph_max: float = 9.0
    alert_do_min: float = 2.0
    alert_nh3n_max: float = 2.0
    alert_turbidity_max: float = 10.0
    alert_cod_max: float = 40.0

    # Database
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "water_quality"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    # JWT
    jwt_secret: str = "water-quality-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    # Logging
    log_level: str = "INFO"
    log_dir: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_paths()
        self._load_config_file()

    def _init_paths(self):
        """Initialize directory paths."""
        base = Path(self.data_dir)
        self.raw_data_dir = str(base / "raw")
        self.cleaned_data_dir = str(base / "cleaned")
        self.sample_data_dir = str(base / "samples")
        self.model_dir = str(base.parent / "models")
        self.log_dir = str(base.parent / "logs")

        for d in [self.raw_data_dir, self.cleaned_data_dir, self.model_dir, self.log_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

    def _load_config_file(self):
        """Load settings from YAML config file if exists."""
        config_file = Path(__file__).parent.parent / "config.yaml"
        if config_file.exists():
            with open(config_file) as f:
                data = yaml.safe_load(f)
            if data:
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)


settings = Settings()
