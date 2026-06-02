"""Shared test fixtures for water quality system tests."""

import json
from pathlib import Path
from typing import Optional

import pandas as pd
import pytest
from httpx import ASGITransport, Client


# ── Sample Data Fixtures ──────────────────────────────────────

@pytest.fixture
def sample_df():
    """10-row, 2-station water quality DataFrame for unit tests."""
    return pd.DataFrame({
        "station_id": ["ST001"] * 5 + ["ST002"] * 5,
        "collection_time": (
            pd.date_range("2026-05-01", periods=5, freq="D").tolist()
            + pd.date_range("2026-05-01", periods=5, freq="D").tolist()
        ),
        "ph": [7.2, 7.1, 8.0, 6.8, 7.5, 7.0, 7.3, 7.8, 6.5, 7.9],
        "do": [6.5, 5.8, 7.0, 4.5, 6.0, 5.5, 6.2, 6.8, 3.0, 5.0],
        "nh3n": [0.15, 0.22, 0.30, 0.10, 0.18, 0.25, 0.12, 0.28, 0.35, 0.08],
        "cod": [10.0, 15.0, 25.0, 8.0, 12.0, 18.0, 20.0, 30.0, 5.0, 14.0],
        "turbidity": [3.2, 4.1, 5.5, 2.0, 3.8, 4.5, 3.0, 6.0, 1.5, 4.0],
        "temperature": [22.5, 23.0, 21.0, 24.0, 22.0, 23.5, 22.8, 21.5, 25.0, 22.0],
        "total_phosphorus": [0.05, 0.08, 0.12, 0.03, 0.06, 0.10, 0.04, 0.15, 0.02, 0.07],
    })


@pytest.fixture
def sample_df_with_alerts():
    """DataFrame with out-of-range values guaranteed to trigger alerts."""
    return pd.DataFrame({
        "station_id": ["ST001", "ST002"],
        "collection_time": ["2026-05-01 08:00:00", "2026-05-01 09:00:00"],
        "ph": [5.5, 9.5],          # < 6.0 (critical), > 9.0 (critical)
        "do": [1.5, 0.5],          # < 2.0 (critical)
        "nh3n": [3.0, 0.5],        # > 2.0 (critical, one only)
        "cod": [50.0, 10.0],       # > 40.0 (critical)
        "turbidity": [12.0, 3.0],  # > 10.0 (warning)
    })


@pytest.fixture
def sample_training_df():
    """60-row (30 days x 2 stations) DataFrame suitable for XGBoost training tests."""
    import numpy as np
    np.random.seed(42)
    stations = ["ST001", "ST002"]
    rows = []
    for sid in stations:
        for day in range(30):
            rows.append({
                "station_id": sid,
                "collection_time": f"2026-05-{day + 1:02d} 08:00:00",
                "ph": round(7.0 + float(np.random.normal(0, 0.5)), 2),
                "do": round(6.0 + float(np.random.normal(0, 0.8)), 2),
                "nh3n": round(0.2 + float(np.random.exponential(0.1)), 3),
                "cod": round(15.0 + float(np.random.gamma(2, 5)), 1),
                "turbidity": round(4.0 + float(np.random.exponential(1.5)), 1),
                "temperature": round(22.0 + float(np.random.normal(0, 2)), 1),
                "total_phosphorus": round(0.08 + float(np.random.exponential(0.05)), 3),
            })
    return pd.DataFrame(rows)


# ── Temp Directory Fixtures ──────────────────────────────────

@pytest.fixture
def temp_data_dir():
    """Provide a temporary directory path for test isolation."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix="wq_test_") as d:
        yield Path(d)


# ── JWT / Auth Fixtures ──────────────────────────────────────

@pytest.fixture
def valid_token():
    """Return a valid JWT token for the admin user."""
    from src.admin.auth import create_access_token
    return create_access_token({"sub": "admin", "role": "admin"})


@pytest.fixture
def viewer_token():
    """Return a valid JWT token for a viewer user."""
    from src.admin.auth import create_access_token
    return create_access_token({"sub": "viewer_user", "role": "viewer"})


@pytest.fixture
def auth_headers(valid_token):
    """Authorization header dict for admin user."""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def viewer_headers(viewer_token):
    """Authorization header dict for viewer user."""
    return {"Authorization": f"Bearer {viewer_token}"}


# ── FastAPI TestClient Fixture ───────────────────────────────

@pytest.fixture(scope="session")
def app():
    """Build the FastAPI app once per test session."""
    from src.main import app
    return app


@pytest.fixture
def client(app):
    """Create an httpx TestClient per test function."""
    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as c:
        yield c
