"""FastAPI application entry point for Water Quality Monitoring & Prediction System."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.routes import data_routes, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # Startup: ensure data directories exist
    Path(settings.raw_data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.cleaned_data_dir).mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, tags=["System"])
app.include_router(data_routes.router, prefix="/api/data", tags=["Data Management"])


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
