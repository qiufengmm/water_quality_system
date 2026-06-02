"""Unit tests for authentication, user management, and station management."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import HTTPException

from src.admin.auth import (
    Station,
    StationManager,
    User,
    UserManager,
    create_access_token,
    require_role,
    verify_token,
)
from src.admin import auth as auth_module
from src.config import settings


@pytest.fixture(autouse=True)
def isolate_persistence(tmp_path, monkeypatch):
    """Redirect _USERS_PATH and _STATIONS_PATH to temp files and reinitialize singletons."""

    users_file = tmp_path / "users.json"
    stations_file = tmp_path / "stations.json"

    monkeypatch.setattr(auth_module, "_USERS_PATH", users_file)
    monkeypatch.setattr(auth_module, "_STATIONS_PATH", stations_file)

    # Save original singletons state references
    old_user_mgr = auth_module.user_manager
    old_station_mgr = auth_module.station_manager

    # Reinitialize user_manager with new temp path
    old_user_mgr._users = {}
    old_user_mgr._load()

    # Reinitialize station_manager with new temp path
    old_station_mgr._stations = {}
    old_station_mgr._load()

    yield


# ── UserManager Init ─────────────────────────────────────────

class TestUserManagerInit:
    """Tests for UserManager initialization."""

    def test_default_admin_exists(self):
        """Admin user present with role 'admin'."""
        um = UserManager()
        admin = um.get_user("admin")
        assert admin is not None
        assert admin.role == "admin"

    def test_default_admin_not_disabled(self):
        """Admin user is not disabled."""
        um = UserManager()
        admin = um.get_user("admin")
        assert admin is not None
        assert admin.disabled is False

    def test_list_users_excludes_password(self):
        """list_users() does not expose password_hash."""
        um = UserManager()
        users = um.list_users()
        for u in users:
            assert "password_hash" not in u

    def test_list_users_contains_admin(self):
        """Admin appears in user list."""
        um = UserManager()
        users = um.list_users()
        usernames = [u["username"] for u in users]
        assert "admin" in usernames


# ── UserManager Authenticate ─────────────────────────────────

class TestUserManagerAuthenticate:
    """Tests for user authentication."""

    def test_valid_credentials(self):
        """Correct username+password returns User object."""
        um = UserManager()
        user = um.authenticate("admin", "admin123")
        assert user is not None
        assert user.username == "admin"

    def test_wrong_password(self):
        """Wrong password returns None."""
        um = UserManager()
        user = um.authenticate("admin", "wrong_password")
        assert user is None

    def test_unknown_username(self):
        """Non-existent username returns None."""
        um = UserManager()
        user = um.authenticate("nonexistent", "password")
        assert user is None

    def test_disabled_user_rejected(self):
        """Disabled user cannot authenticate."""
        um = UserManager()
        # Create a disabled user
        um.create_user("disabled_user", "password123", role="viewer")
        user = um.get_user("disabled_user")
        user.disabled = True
        result = um.authenticate("disabled_user", "password123")
        assert result is None

    def test_password_hash_is_bcrypt(self):
        """Stored hash starts with '$2b$'."""
        um = UserManager()
        admin = um.get_user("admin")
        assert admin.password_hash.startswith("$2b$")


# ── UserManager CRUD ─────────────────────────────────────────

class TestUserManagerCRUD:
    """Tests for user CRUD operations."""

    def test_create_user(self):
        """Returns True, user is retrievable."""
        um = UserManager()
        result = um.create_user("newuser", "pass123", role="editor", display_name="New User")
        assert result is True
        assert um.get_user("newuser") is not None

    def test_create_duplicate_user(self):
        """Returns False for duplicate username."""
        um = UserManager()
        um.create_user("dupuser", "pass123")
        result = um.create_user("dupuser", "pass456")
        assert result is False

    def test_get_user_nonexistent(self):
        """Returns None for unknown user."""
        um = UserManager()
        assert um.get_user("no_such_user") is None


# ── StationManager Init ──────────────────────────────────────

class TestStationManagerInit:
    """Tests for StationManager initialization."""

    def test_default_stations_exist(self):
        """ST001, ST002, ST003 exist."""
        sm = StationManager()
        stations = sm.list_stations()
        ids = [s["station_id"] for s in stations]
        for sid in ("ST001", "ST002", "ST003"):
            assert sid in ids

    def test_default_stations_have_names(self):
        """Default stations have Chinese names."""
        sm = StationManager()
        for s in sm.list_stations():
            assert s["name"] != ""


# ── StationManager CRUD ──────────────────────────────────────

class TestStationManagerCRUD:
    """Tests for station CRUD operations."""

    def test_add_station(self):
        """New station appears in list."""
        sm = StationManager()
        new_station = Station("ST099", "Test Station", "Test Location")
        result = sm.add_station(new_station)
        assert result is True
        ids = [s["station_id"] for s in sm.list_stations()]
        assert "ST099" in ids

    def test_add_duplicate_station(self):
        """Returns False when station_id exists."""
        sm = StationManager()
        dup = Station("ST001", "Duplicate")
        result = sm.add_station(dup)
        assert result is False

    def test_get_station(self):
        """Returns correct Station by ID."""
        sm = StationManager()
        station = sm.get_station("ST001")
        assert station is not None
        assert station.station_id == "ST001"

    def test_get_station_nonexistent(self):
        """Returns None for unknown ID."""
        sm = StationManager()
        assert sm.get_station("ST999") is None

    def test_update_station(self):
        """Fields updated and persisted."""
        sm = StationManager()
        result = sm.update_station("ST001", {"name": "Updated Name"})
        assert result is True
        station = sm.get_station("ST001")
        assert station.name == "Updated Name"

    def test_update_nonexistent_station(self):
        """Returns False for unknown station."""
        sm = StationManager()
        result = sm.update_station("ST999", {"name": "Nope"})
        assert result is False

    def test_delete_station(self):
        """Station removed from list."""
        sm = StationManager()
        sm.add_station(Station("ST_TMP", "Temp"))
        result = sm.delete_station("ST_TMP")
        assert result is True
        assert sm.get_station("ST_TMP") is None

    def test_delete_nonexistent(self):
        """Returns False for unknown station."""
        sm = StationManager()
        result = sm.delete_station("ST999")
        assert result is False


# ── JWT Functions ────────────────────────────────────────────

class TestJWT:
    """Tests for JWT token creation and verification."""

    def test_create_access_token(self):
        """Returns a string token with dots (JWT format)."""
        token = create_access_token({"sub": "testuser"})
        assert isinstance(token, str)
        assert token.count(".") == 2

    def test_verify_valid_token(self):
        """Decoded payload matches original data."""
        original = {"sub": "testuser", "role": "admin"}
        token = create_access_token(original)
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    def test_verify_invalid_token(self):
        """Returns None for garbage token."""
        payload = verify_token("invalid.token.string")
        assert payload is None

    def test_verify_expired_token(self):
        """Token with past exp returns None."""
        from jose import jwt as jose_jwt
        expired = jose_jwt.encode(
            {"sub": "testuser", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        payload = verify_token(expired)
        assert payload is None

    def test_token_contains_sub_claim(self):
        """Payload has 'sub' key matching username."""
        token = create_access_token({"sub": "testuser"})
        payload = verify_token(token)
        assert payload["sub"] == "testuser"


# ── require_role Function ────────────────────────────────────

class TestRequireRole:
    """Tests for role-checking dependency factory."""

    @staticmethod
    def _make_user(role: str) -> User:
        return User(username=f"{role}_user", password_hash="hash", role=role)

    @pytest.mark.asyncio
    async def test_admin_can_access_admin_role(self):
        """Admin user passes require_role('admin')."""
        checker = require_role("admin")
        user = self._make_user("admin")
        result = await checker(user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_admin_can_access_any_role(self):
        """Admin user passes require_role('editor')."""
        checker = require_role("editor")
        user = self._make_user("admin")
        result = await checker(user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_viewer_rejected_for_admin(self):
        """Viewer user raises 403 for require_role('admin')."""
        checker = require_role("admin")
        user = self._make_user("viewer")
        with pytest.raises(HTTPException) as exc:
            await checker(user=user)
        assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_none_user_raises_401(self):
        """None user raises 401."""
        checker = require_role("admin")
        with pytest.raises(HTTPException) as exc:
            await checker(user=None)
        assert exc.value.status_code == 401
