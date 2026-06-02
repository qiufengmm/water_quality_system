"""JWT authentication and user management.

Provides token-based authentication with role-based access control
(admin, editor, viewer). Users are stored in a JSON file for
simplicity (no database dependency).
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# ── bcrypt compat shim: passlib 1.7.4 reads bcrypt.__about__.__version__
# which bcrypt >= 4.1 removed.  Re-expose it so passlib doesn't warn.
import bcrypt as _bcrypt
if not hasattr(_bcrypt, "__about__"):
    class _About:
        __version__ = _bcrypt.__version__
    _bcrypt.__about__ = _About

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token scheme
security = HTTPBearer(auto_error=False)

# User storage path
_USERS_PATH = Path(settings.data_dir) / "users.json"
_STATIONS_PATH = Path(settings.data_dir) / "stations.json"


@dataclass
class User:
    """Application user with role-based access."""
    username: str
    password_hash: str
    role: str = "viewer"       # "admin", "editor", "viewer"
    display_name: str = ""
    disabled: bool = False


@dataclass
class Station:
    """Monitoring station information."""
    station_id: str
    name: str = ""
    location: str = ""
    description: str = ""
    contact: str = ""


class UserManager:
    """Manages user accounts with JSON file persistence."""

    def __init__(self):
        self._users: dict[str, User] = {}
        self._load()

    def _load(self):
        """Load users from JSON file."""
        if _USERS_PATH.exists():
            try:
                with open(_USERS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for u in data:
                    user = User(**u)
                    self._users[user.username] = user
            except Exception:
                pass

        # Ensure default admin exists
        if "admin" not in self._users:
            self._users["admin"] = User(
                username="admin",
                password_hash=pwd_context.hash("admin123"),
                role="admin",
                display_name="系统管理员",
            )
            self._save()

    def _save(self):
        """Persist users to JSON file."""
        _USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(u) for u in self._users.values()]
        with open(_USERS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Verify credentials and return user if valid."""
        user = self._users.get(username)
        if not user or user.disabled:
            return None
        if not pwd_context.verify(password, user.password_hash):
            return None
        return user

    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def list_users(self) -> list[dict]:
        """List all users (password hashes excluded)."""
        result = []
        for u in self._users.values():
            result.append({
                "username": u.username,
                "role": u.role,
                "display_name": u.display_name,
                "disabled": u.disabled,
            })
        return result

    def create_user(self, username: str, password: str,
                    role: str = "viewer", display_name: str = "") -> bool:
        """Create a new user. Returns False if username exists."""
        if username in self._users:
            return False
        self._users[username] = User(
            username=username,
            password_hash=pwd_context.hash(password),
            role=role,
            display_name=display_name or username,
        )
        self._save()
        return True


class StationManager:
    """Manages monitoring station metadata."""

    def __init__(self):
        self._stations: dict[str, Station] = {}
        self._load()

    def _load(self):
        """Load stations from JSON file."""
        if _STATIONS_PATH.exists():
            try:
                with open(_STATIONS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for s in data:
                    station = Station(**s)
                    self._stations[station.station_id] = station
            except Exception:
                pass

        # Ensure default stations exist
        defaults = {
            "ST001": Station("ST001", "上游监测站", "河流上游", "河流入口处水质监测", "张三-13800000001"),
            "ST002": Station("ST002", "中游监测站", "河流中游", "城市段水质监测", "李四-13800000002"),
            "ST003": Station("ST003", "下游监测站", "河流下游", "河流出口处水质监测", "王五-13800000003"),
        }
        changed = False
        for sid, s in defaults.items():
            if sid not in self._stations:
                self._stations[sid] = s
                changed = True
        if changed:
            self._save()

    def _save(self):
        """Persist stations to JSON file."""
        _STATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(s) for s in self._stations.values()]
        with open(_STATIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def list_stations(self) -> list[dict]:
        return [asdict(s) for s in self._stations.values()]

    def get_station(self, station_id: str) -> Optional[Station]:
        return self._stations.get(station_id)

    def add_station(self, station: Station) -> bool:
        if station.station_id in self._stations:
            return False
        self._stations[station.station_id] = station
        self._save()
        return True

    def update_station(self, station_id: str, data: dict) -> bool:
        station = self._stations.get(station_id)
        if not station:
            return False
        for key, value in data.items():
            if hasattr(station, key) and value is not None:
                setattr(station, key, value)
        self._save()
        return True

    def delete_station(self, station_id: str) -> bool:
        if station_id not in self._stations:
            return False
        del self._stations[station_id]
        self._save()
        return True


# ── JWT Helpers ──────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """FastAPI dependency to extract current user from token.

    Returns None if no token provided (for optional auth).
    Raises 401 if token is invalid.
    """
    if credentials is None:
        return None
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = user_manager.get_user(username)
    if user is None or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
        )
    return user


def require_role(required_role: str):
    """Factory for role-checking dependency.

    Usage:
        @router.get("/admin/users")
        async def list_users(user: User = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(user: Optional[User] = Depends(get_current_user)):
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        if user.role not in ("admin", required_role) and user.role != "admin":
            # admin has access to everything
            if user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{required_role}' required, got '{user.role}'",
                )
        return user
    return role_checker


# Singletons
user_manager = UserManager()
station_manager = StationManager()
