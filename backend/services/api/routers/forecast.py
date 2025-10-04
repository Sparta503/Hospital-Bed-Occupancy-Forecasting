from fastapi import APIRouter, HTTPException
from ..schemas import PredictionRequest, ForecastResponse, ErrorResponse
from typing import Any
from uuid import uuid4
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/forecast", response_model=ForecastResponse, responses={400: {"model": ErrorResponse}})
async def forecast_bed_occupancy(request: PredictionRequest) -> Any:
    """
    Forecast hospital bed occupancy for a given ward and time period.
    """
from fastapi import APIRouter, HTTPException
from ..schemas import PredictionRequest, ForecastResponse, ErrorResponse
from typing import Any
from uuid import uuid4
from datetime import datetime, timedelta
import joblib
import pandas as pd
import os

router = APIRouter()

# Load model once at startup (XGBoost example)
MODEL_PATH = os.environ.get("XGB_MODEL_PATH", "xgb_model_latest.joblib")
try:
    xgb_model = joblib.load(MODEL_PATH)
except Exception as e:
    xgb_model = None
    print(f"Warning: Could not load XGBoost model from {MODEL_PATH}: {e}")

@router.post("/forecast", response_model=ForecastResponse, responses={400: {"model": ErrorResponse}})
async def forecast_bed_occupancy(request: PredictionRequest) -> Any:
    """
    Forecast hospital bed occupancy for a given ward and time period using a trained XGBoost model.
    """
    try:
        if xgb_model is None:
            raise HTTPException(status_code=500, detail="Model not loaded. Contact administrator.")
        # Prepare features for prediction (update as needed to match your model's training features)
        features = []
        for i in range(request.days_ahead):
            features.append({
                "feature1": request.current_occupied_beds,  # Replace with real features
                "feature2": i+1  # Example: days ahead
            })
        X_pred = pd.DataFrame(features)
        y_pred = xgb_model.predict(X_pred)
        predictions = []
        for i, pred in enumerate(y_pred):
            pred_date = request.record_date + timedelta(days=i+1)
            predictions.append({
                "prediction_date": pred_date,
                "predicted_occupied_beds": float(pred),
                "confidence_lower": None,
                "confidence_upper": None,
                "confidence_score": None,
                "occupancy_rate": min(1.0, float(pred) / request.bed_count)
            })
        response = ForecastResponse(
            request_id=str(uuid4()),
            hospital_id=request.hospital_id,
            ward_id=request.ward_id,
            model_id=request.model_id or "xgb_model_latest",
            model_type="xgboost",
            base_date=request.record_date,
            forecast_horizon_days=request.days_ahead,
            predictions=predictions,
            created_at=datetime.now(),
            metadata={"note": "Prediction from trained XGBoost model."}
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))