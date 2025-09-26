"""
Data schemas and models for hospital bed occupancy forecasting system.

This module contains Pydantic models for:
- Input validation
- API request/response schemas
- Data transformation models
- Model training and evaluation schemas
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator, confloat, conint
import pandas as pd

# Enums
class ModelType(str, Enum):
    """Available model types for forecasting"""
    XGBOOST = "xgboost"
    PROPHET = "prophet"
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    LSTM = "lstm"

class PredictionHorizon(str, Enum):
    """Prediction time horizons"""
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-6 months

class WardType(str, Enum):
    """Types of hospital wards"""
    ICU = "icu"
    EMERGENCY = "emergency"
    GENERAL = "general"
    PEDIATRIC = "pediatric"
    MATERNITY = "maternity"
    SURGICAL = "surgical"
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"

# Input Schemas
class BedOccupancyInput(BaseModel):
    """Input schema for bed occupancy data"""
    hospital_id: str = Field(..., description="Unique identifier for the hospital")
    ward_id: str = Field(..., description="Ward or department identifier")
    ward_type: Optional[WardType] = Field(None, description="Type of ward")
    bed_count: conint(ge=1) = Field(..., description="Total number of beds in the ward")
    occupied_beds: conint(ge=0) = Field(..., description="Number of occupied beds")
    record_date: datetime = Field(..., description="The date this occupancy record is for")
    admission_rate: Optional[confloat(ge=0, le=1)] = Field(None, description="Daily admission rate")
    discharge_rate: Optional[confloat(ge=0, le=1)] = Field(None, description="Daily discharge rate")
    seasonality_factor: Optional[confloat(ge=0, le=2)] = Field(None, description="Seasonal adjustment factor")
    
    @validator('occupied_beds')
    def validate_occupied_beds(cls, v, values):
        if 'bed_count' in values and v > values['bed_count']:
            raise ValueError('Occupied beds cannot exceed total bed count')
        return v
    
    @validator('record_date')
    def validate_record_date(cls, v):
        if v > datetime.now():
            raise ValueError('Record date cannot be in the future')
        return v

class PredictionRequest(BaseModel):
    """Request schema for making predictions"""
    hospital_id: str = Field(..., description="Hospital identifier")
    ward_id: str = Field(..., description="Ward identifier")
    ward_type: Optional[WardType] = Field(None, description="Type of ward")
    bed_count: conint(ge=1) = Field(..., description="Total number of beds")
    current_occupied_beds: conint(ge=0) = Field(..., description="Current occupied beds")
    record_date: datetime = Field(..., description="Base date for prediction")
    days_ahead: conint(ge=1, le=90) = Field(7, description="Number of days to forecast")
    model_id: Optional[str] = Field(None, description="Specific model ID to use")
    include_confidence: bool = Field(True, description="Include confidence intervals")
    
    @validator('current_occupied_beds')
    def validate_current_occupied_beds(cls, v, values):
        if 'bed_count' in values and v > values['bed_count']:
            raise ValueError('Current occupied beds cannot exceed total bed count')
        return v

class TrainingRequest(BaseModel):
    """Request schema for model training"""
    model_name: str = Field(..., description="Name for the trained model")
    model_type: ModelType = Field(..., description="Type of model to train")
    hospital_id: Optional[str] = Field(None, description="Hospital-specific model")
    ward_id: Optional[str] = Field(None, description="Ward-specific model")
    ward_type: Optional[WardType] = Field(None, description="Ward type filter")
    start_date: Optional[datetime] = Field(None, description="Training data start date")
    end_date: Optional[datetime] = Field(None, description="Training data end date")
    features: List[str] = Field(default_factory=list, description="Features to use for training")
    target_variable: str = Field("occupied_beds", description="Target variable to predict")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Model hyperparameters")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

# Output Schemas
class PredictionResult(BaseModel):
    """Single prediction result"""
    prediction_date: datetime = Field(..., description="Date for this prediction")
    predicted_occupied_beds: confloat(ge=0) = Field(..., description="Predicted number of occupied beds")
    confidence_lower: Optional[confloat(ge=0)] = Field(None, description="Lower confidence bound")
    confidence_upper: Optional[confloat(ge=0)] = Field(None, description="Upper confidence bound")
    confidence_score: confloat(ge=0, le=1) = Field(..., description="Confidence score (0-1)")
    occupancy_rate: confloat(ge=0, le=1) = Field(..., description="Predicted occupancy rate")
    
    @validator('occupancy_rate')
    def calculate_occupancy_rate(cls, v, values):
        if 'predicted_occupied_beds' in values:
            # This would need bed_count context, simplified for now
            return min(v, 1.0)
        return v

class ForecastResponse(BaseModel):
    """Complete forecast response"""
    request_id: str = Field(..., description="Unique request identifier")
    hospital_id: str = Field(..., description="Hospital identifier")
    ward_id: str = Field(..., description="Ward identifier")
    model_id: str = Field(..., description="Model used for prediction")
    model_type: ModelType = Field(..., description="Type of model used")
    base_date: datetime = Field(..., description="Base date for forecast")
    forecast_horizon_days: conint(ge=1) = Field(..., description="Number of days forecasted")
    predictions: List[PredictionResult] = Field(..., description="Daily predictions")
    created_at: datetime = Field(default_factory=datetime.now, description="When forecast was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ModelMetrics(BaseModel):
    """Model performance metrics"""
    rmse: confloat(ge=0) = Field(..., description="Root Mean Square Error")
    mae: confloat(ge=0) = Field(..., description="Mean Absolute Error")
    mape: confloat(ge=0) = Field(..., description="Mean Absolute Percentage Error")
    r2_score: confloat(le=1) = Field(..., description="R-squared score")
    training_samples: conint(ge=1) = Field(..., description="Number of training samples")
    validation_samples: conint(ge=0) = Field(..., description="Number of validation samples")
    
class ModelInfo(BaseModel):
    """Model information and metadata"""
    model_id: str = Field(..., description="Unique model identifier")
    model_name: str = Field(..., description="Human-readable model name")
    model_type: ModelType = Field(..., description="Type of model")
    hospital_id: Optional[str] = Field(None, description="Hospital-specific model")
    ward_id: Optional[str] = Field(None, description="Ward-specific model")
    ward_type: Optional[WardType] = Field(None, description="Ward type")
    status: str = Field(..., description="Model status (active, inactive, training)")
    created_at: datetime = Field(..., description="When model was created")
    last_trained: Optional[datetime] = Field(None, description="Last training date")
    metrics: Optional[ModelMetrics] = Field(None, description="Model performance metrics")
    features: List[str] = Field(..., description="Features used by model")
    target_variable: str = Field(..., description="Target variable")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Model hyperparameters")
    version: str = Field(..., description="Model version")

class TrainingResponse(BaseModel):
    """Response from model training"""
    model_id: str = Field(..., description="ID of the trained model")
    model_name: str = Field(..., description="Name of the trained model")
    model_type: ModelType = Field(..., description="Type of model trained")
    training_status: str = Field(..., description="Training status")
    training_duration_seconds: Optional[confloat(ge=0)] = Field(None, description="Training duration")
    metrics: Optional[ModelMetrics] = Field(None, description="Training metrics")
    training_samples: conint(ge=0) = Field(..., description="Number of samples used")
    features_used: List[str] = Field(..., description="Features used in training")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Hyperparameters used")
    created_at: datetime = Field(default_factory=datetime.now, description="When training completed")

# API Response Schemas
class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
class PaginatedResponse(ApiResponse):
    """Paginated API response"""
    page: conint(ge=1) = Field(..., description="Current page number")
    page_size: conint(ge=1) = Field(..., description="Number of items per page")
    total_items: conint(ge=0) = Field(..., description="Total number of items")
    total_pages: conint(ge=0) = Field(..., description="Total number of pages")

# Error Schemas
class ErrorResponse(BaseModel):
    """Error response schema"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")