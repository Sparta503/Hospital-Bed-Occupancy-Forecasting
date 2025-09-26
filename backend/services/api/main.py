"""
Main FastAPI application for hospital bed occupancy forecasting system.

This module sets up the FastAPI app and includes all API routers.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time
from datetime import datetime

from . import api_router
from .schemas import ErrorResponse, ApiResponse
from ..serving import model_registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Hospital Bed Occupancy Forecasting API",
    description="API for forecasting hospital bed occupancy using machine learning models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response details
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=f"HTTP_{exc.status_code}",
            error_message=exc.detail,
            details={"path": str(request.url)}
        ).dict()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            error_message="Request validation failed",
            details={"errors": exc.errors()}
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected Error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            error_message="An unexpected error occurred",
            details={"path": str(request.url)}
        ).dict()
    )

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/", response_model=ApiResponse)
async def root():
    """Root endpoint with API information"""
    return ApiResponse(
        success=True,
        message="Hospital Bed Occupancy Forecasting API",
        data={
            "version": "1.0.0",
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "timestamp": datetime.now().isoformat()
        }
    )

# Health check endpoint
@app.get("/health", response_model=ApiResponse)
async def health_check():
    """Comprehensive health check"""
    try:
        # Check database connection (if applicable)
        db_status = "healthy"
        
        # Check model registry
        try:
            active_models = model_registry.get_active_models()
            model_status = "healthy" if active_models else "no_models"
        except Exception as e:
            model_status = f"error: {str(e)}"
        
        return ApiResponse(
            success=True,
            message="System health check completed",
            data={
                "status": "healthy",
                "database": db_status,
                "model_registry": model_status,
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error_code="HEALTH_CHECK_FAILED",
                error_message="System health check failed",
                details={"error": str(e)}
            ).dict()
        )

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Hospital Bed Occupancy Forecasting API")
    
    # Initialize model registry
    try:
        logger.info("Initializing model registry...")
        # Model registry is already initialized via import
        active_models = model_registry.get_active_models()
        logger.info(f"Found {len(active_models)} active models")
    except Exception as e:
        logger.error(f"Failed to initialize model registry: {str(e)}")

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown"""
    logger.info("Shutting down Hospital Bed Occupancy Forecasting API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)