"""
API module for hospital bed occupancy forecasting system.

This module provides FastAPI routers for:
- Health checks
- Bed occupancy data management
- Prediction endpoints
- Model training endpoints
- Model management
"""

from fastapi import APIRouter
from .health import router as health_router
from .occupancy import router as occupancy_router
from .schemas import (
    # Input schemas
    BedOccupancyInput,
    PredictionRequest,
    TrainingRequest,
    # Output schemas
    PredictionResult,
    ForecastResponse,
    ModelMetrics,
    ModelInfo,
    TrainingResponse,
    # API response schemas
    ApiResponse,
    PaginatedResponse,
    ErrorResponse,
    # Enums
    ModelType,
    PredictionHorizon,
    WardType
)

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(occupancy_router, prefix="/occupancy", tags=["occupancy"])

# Export all routers and schemas
__all__ = [
    "api_router",
    "health_router",
    "occupancy_router",
    # Input schemas
    "BedOccupancyInput",
    "PredictionRequest", 
    "TrainingRequest",
    # Output schemas
    "PredictionResult",
    "ForecastResponse",
    "ModelMetrics",
    "ModelInfo",
    "TrainingResponse",
    # API response schemas
    "ApiResponse",
    "PaginatedResponse",
    "ErrorResponse",
    # Enums
    "ModelType",
    "PredictionHorizon",
    "WardType"
]