"""Health check and system information endpoints."""

from datetime import datetime

from fastapi import APIRouter

from src.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "app": settings.app_name,
    }
