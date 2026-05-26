"""Health check and system information endpoints."""

from datetime import datetime

from fastapi import APIRouter

from src.config import settings
from src.data_manager import data_manager

router = APIRouter()


@router.get("/health")
async def health_check():
    """System health check endpoint with data status."""
    data_info = data_manager.get_data_info()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "app": settings.app_name,
        "data": data_info,
    }
