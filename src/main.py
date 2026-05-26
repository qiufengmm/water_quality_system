"""FastAPI application entry point for Water Quality Monitoring & Prediction System."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.routes import data_routes, health, export_routes, predict_routes, alert_routes, admin_routes
from src.data_manager import data_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    Path(settings.raw_data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.cleaned_data_dir).mkdir(parents=True, exist_ok=True)
    info = data_manager.get_data_info()
    if info.get("has_raw"):
        print(f"  Loaded {info['raw_records']} raw records from disk")
    if info.get("has_cleaned"):
        print(f"  Loaded {info['cleaned_records']} cleaned records from disk")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["System"])
app.include_router(data_routes.router, prefix="/api/data", tags=["Data Management"])
app.include_router(export_routes.router, prefix="/api/export", tags=["Data Export"])
app.include_router(predict_routes.router, prefix="/api", tags=["Prediction"])
app.include_router(alert_routes.router, prefix="/api", tags=["Alert"])
app.include_router(admin_routes.router, prefix="/api", tags=["Admin"])


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
