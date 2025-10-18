"""
Routers package for the Hospital Bed Occupancy Forecasting API.
"""

from .forecast import router as forecast_router
from .occupancy import router as occupancy_router

__all__ = ["forecast_router", "occupancy_router"]
