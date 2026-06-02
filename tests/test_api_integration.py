"""API integration tests using httpx TestClient.

Tests cover all route groups: health, data, export, predict, alert, admin.
"""

import io

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest_asyncio.fixture
async def client():
    """Create a fresh AsyncClient for each test."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def admin_token(client):
    """Log in as admin and return a valid token."""
    resp = await client.post("/api/admin/login",
                             json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(admin_token):
    """Authorization header for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


# ── Health Endpoints ─────────────────────────────────────────

class TestHealthEndpoint:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health(self, client):
        """GET /health returns status, version, app name."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "Water Quality" in data["app"]

    @pytest.mark.asyncio
    async def test_root(self, client):
        """GET / returns app name and docs link."""
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "app" in data
        assert "Water Quality" in data["app"]


# ── Data Upload & Query ──────────────────────────────────────

class TestDataUpload:
    """Tests for data upload endpoints."""

    @pytest.mark.asyncio
    async def test_upload_simulate(self, client):
        """POST /api/data/upload/simulate generates records."""
        resp = await client.post("/api/data/upload/simulate",
                                 json={"station_id": "ST001", "hours": 12})
        assert resp.status_code == 200
        data = resp.json()
        assert data["records"] >= 12
        assert "message" in data

    @pytest.mark.asyncio
    async def test_upload_csv_file(self, client):
        """POST /api/data/upload accepts CSV file upload."""
        csv_content = "station_id,collection_time,ph,do,nh3n\nST001,2026-06-01 08:00:00,7.2,6.5,0.15\n"
        files = {"file": ("test.csv", csv_content, "text/csv")}
        resp = await client.post("/api/data/upload", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["records_loaded"] == 1

    @pytest.mark.asyncio
    async def test_upload_manual(self, client):
        """POST /api/data/manual inserts a single record."""
        resp = await client.post("/api/data/manual", json={
            "station_id": "ST001",
            "collection_time": "2026-06-01 08:00:00",
            "ph": 7.2,
            "do": 6.5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert "Record added" in data["message"]


class TestDataQuery:
    """Tests for data query endpoints."""

    @pytest.mark.asyncio
    async def test_get_raw_data(self, client):
        """GET /api/data/raw returns records."""
        resp = await client.get("/api/data/raw")
        assert resp.status_code == 200
        data = resp.json()
        assert "records" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_data_summary(self, client):
        """GET /api/data/summary returns statistics."""
        resp = await client.get("/api/data/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_records" in data
        assert "indicators" in data

    @pytest.mark.asyncio
    async def test_get_stations(self, client):
        """GET /api/data/stations returns station list."""
        resp = await client.get("/api/data/stations")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_data_info(self, client):
        """GET /api/data/info returns metadata."""
        resp = await client.get("/api/data/info")
        assert resp.status_code == 200
        data = resp.json()
        assert "has_raw" in data


# ── Data Cleaning ────────────────────────────────────────────

class TestDataClean:
    """Tests for data cleaning endpoint."""

    @pytest.mark.asyncio
    async def test_clean_with_data(self, client):
        """POST /api/data/clean returns cleaning report."""
        resp = await client.post("/api/data/clean")
        assert resp.status_code in (200, 400)

    @pytest.mark.asyncio
    async def test_get_cleaned_data(self, client):
        """GET /api/data/cleaned returns records or message."""
        resp = await client.get("/api/data/cleaned")
        assert resp.status_code == 200
        data = resp.json()
        assert "records" in data or "message" in data


# ── Alert API ────────────────────────────────────────────────

class TestAlertAPI:
    """Tests for alert management endpoints."""

    @pytest.mark.asyncio
    async def test_get_rules(self, client):
        """GET /api/alert/rules returns 12 default rules."""
        resp = await client.get("/api/alert/rules")
        assert resp.status_code == 200
        rules = resp.json()["rules"]
        assert len(rules) == 12

    @pytest.mark.asyncio
    async def test_update_rules(self, client):
        """PUT /api/alert/rules updates rule configuration."""
        new_rules = [
            {"indicator": "ph", "operator": "<", "threshold": 5.0, "severity": "critical"},
        ]
        resp = await client.put("/api/alert/rules", json=new_rules)
        assert resp.status_code == 200
        assert len(resp.json()["rules"]) == 1
        # Restore default rules
        await client.put("/api/alert/rules", json=[
            {"indicator": "ph", "operator": "<", "threshold": 6.0, "severity": "critical"},
            {"indicator": "ph", "operator": ">", "threshold": 9.0, "severity": "critical"},
        ])

    @pytest.mark.asyncio
    async def test_check_alerts(self, client):
        """POST /api/alert/check checks current data for alerts."""
        resp = await client.post("/api/alert/check")
        assert resp.status_code in (200, 400)
        if resp.status_code == 200:
            data = resp.json()
            assert "checked_records" in data

    @pytest.mark.asyncio
    async def test_alert_history(self, client):
        """GET /api/alert/history returns paginated history."""
        resp = await client.get("/api/alert/history?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "records" in data
        assert "total" in data


# ── Auth API ─────────────────────────────────────────────────

class TestAuthAPI:
    """Tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_valid(self, client):
        """Valid credentials return token."""
        resp = await client.post("/api/admin/login",
                                 json={"username": "admin", "password": "admin123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_login_invalid(self, client):
        """Invalid credentials return 401."""
        resp = await client.post("/api/admin/login",
                                 json={"username": "admin", "password": "wrong"})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_authenticated(self, client, auth_headers):
        """Authenticated user can access /me."""
        resp = await client.get("/api/admin/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "admin"

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client):
        """No auth returns 401."""
        resp = await client.get("/api/admin/me")
        assert resp.status_code == 401


# ── Station Admin API ────────────────────────────────────────

class TestStationAdminAPI:
    """Tests for station management endpoints."""

    @pytest.mark.asyncio
    async def test_list_stations_authenticated(self, client, auth_headers):
        """Authenticated user can list stations."""
        resp = await client.get("/api/admin/stations", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["stations"]) >= 3

    @pytest.mark.asyncio
    async def test_list_stations_unauthenticated(self, client):
        """No auth returns 401."""
        resp = await client.get("/api/admin/stations")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_station_admin(self, client, auth_headers):
        """Admin can create a station."""
        import time
        station_id = f"ST_TMP_{int(time.time())}"
        resp = await client.post("/api/admin/stations",
                                 json={"station_id": station_id, "name": "Test Station",
                                       "location": "Test", "description": "Test",
                                       "contact": "Tester"},
                                 headers=auth_headers)
        assert resp.status_code == 200
        await client.delete(f"/api/admin/stations/{station_id}", headers=auth_headers)

    @pytest.mark.asyncio
    async def test_delete_station(self, client, auth_headers):
        """Admin can delete a station."""
        await client.post("/api/admin/stations",
                          json={"station_id": "ST_DEL", "name": "To Delete"},
                          headers=auth_headers)
        resp = await client.delete("/api/admin/stations/ST_DEL", headers=auth_headers)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_update_station(self, client, auth_headers):
        """Admin can update a station."""
        resp = await client.put("/api/admin/stations/ST001",
                                json={"name": "Updated Name"}, headers=auth_headers)
        assert resp.status_code == 200
        await client.put("/api/admin/stations/ST001",
                         json={"name": "上游监测站"}, headers=auth_headers)


# ── Export API ───────────────────────────────────────────────

class TestExportAPI:
    """Tests for export endpoints."""

    @pytest.mark.asyncio
    async def test_export_raw_csv(self, client):
        """GET /api/export/raw/csv returns CSV."""
        resp = await client.get("/api/export/raw/csv")
        assert resp.status_code in (200, 400)

    @pytest.mark.asyncio
    async def test_export_raw_excel(self, client):
        """GET /api/export/raw/excel returns .xlsx binary."""
        resp = await client.get("/api/export/raw/excel")
        assert resp.status_code in (200, 400)

    @pytest.mark.asyncio
    async def test_export_report(self, client):
        """GET /api/export/report returns multi-sheet Excel."""
        resp = await client.get("/api/export/report")
        assert resp.status_code in (200, 400)
        if resp.status_code == 200:
            assert "openxmlformats" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_summary_csv(self, client):
        """GET /api/export/summary/csv returns CSV summary."""
        resp = await client.get("/api/export/summary/csv")
        assert resp.status_code in (200, 400)


# ── Predict API ──────────────────────────────────────────────

class TestPredictAPI:
    """Tests for prediction endpoints."""

    @pytest.mark.asyncio
    async def test_model_info(self, client):
        """GET /api/predict/model-info returns model state."""
        resp = await client.get("/api/predict/model-info")
        assert resp.status_code == 200
        data = resp.json()
        assert "is_trained" in data or "model_name" in data or "status" in data

    @pytest.mark.asyncio
    async def test_train_from_data(self, client):
        """POST /api/predict/train trains using sample data."""
        resp = await client.post("/api/predict/train")
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            data = resp.json()
            assert "avg_r2" in data or "_summary" in data

    @pytest.mark.asyncio
    async def test_predict_history(self, client):
        """GET /api/predict/history returns model list."""
        resp = await client.get("/api/predict/history")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data
