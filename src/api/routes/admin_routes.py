"""Admin API routes for authentication, user management, and station management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.admin.auth import (
    User, Station,
    user_manager, station_manager,
    create_access_token, get_current_user, require_role,
)

router = APIRouter()


# ── Request/Response Models ─────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "viewer"
    display_name: str = ""


class StationCreate(BaseModel):
    station_id: str
    name: str = ""
    location: str = ""
    description: str = ""
    contact: str = ""


class StationUpdate(BaseModel):
    name: str = None
    location: str = None
    description: str = None
    contact: str = None


# ── Auth Endpoints ──────────────────────────────────────

@router.post("/admin/login")
async def login(req: LoginRequest):
    """Authenticate user and return JWT token."""
    user = user_manager.authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({
        "sub": user.username,
        "role": user.role,
        "display_name": user.display_name,
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "display_name": user.display_name,
    }


@router.post("/admin/register")
async def register(req: RegisterRequest, admin_user: User = Depends(require_role("admin"))):
    """Register a new user (admin only)."""
    success = user_manager.create_user(req.username, req.password, req.role, req.display_name)
    if not success:
        raise HTTPException(status_code=409, detail=f"User '{req.username}' already exists")
    return {"message": f"User '{req.username}' created", "role": req.role}


@router.get("/admin/users")
async def list_users(admin_user: User = Depends(require_role("admin"))):
    """List all users (admin only)."""
    return {"users": user_manager.list_users()}


@router.get("/admin/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "username": user.username,
        "role": user.role,
        "display_name": user.display_name,
    }


# ── Station Management ──────────────────────────────────

@router.get("/admin/stations")
async def list_stations(user: User = Depends(get_current_user)):
    """List all monitoring stations (authentication required)."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"stations": station_manager.list_stations()}


@router.post("/admin/stations")
async def create_station(
    station_data: StationCreate,
    admin_user: User = Depends(require_role("admin")),
):
    """Create a new monitoring station (admin only)."""
    station = Station(
        station_id=station_data.station_id,
        name=station_data.name,
        location=station_data.location,
        description=station_data.description,
        contact=station_data.contact,
    )
    success = station_manager.add_station(station)
    if not success:
        raise HTTPException(status_code=409, detail=f"Station '{station_data.station_id}' already exists")
    return {"message": "Station created", "station": station_data.model_dump()}


@router.put("/admin/stations/{station_id}")
async def update_station(
    station_id: str,
    data: StationUpdate,
    admin_user: User = Depends(require_role("admin")),
):
    """Update a monitoring station (admin only)."""
    success = station_manager.update_station(
        station_id,
        {k: v for k, v in data.model_dump().items() if v is not None},
    )
    if not success:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found")
    return {"message": "Station updated"}


@router.delete("/admin/stations/{station_id}")
async def delete_station(
    station_id: str,
    admin_user: User = Depends(require_role("admin")),
):
    """Delete a monitoring station (admin only)."""
    success = station_manager.delete_station(station_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found")
    return {"message": "Station deleted"}
