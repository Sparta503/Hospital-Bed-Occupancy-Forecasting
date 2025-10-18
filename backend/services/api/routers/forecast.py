from fastapi import APIRouter, HTTPException
from ..schemas import PredictionRequest, ErrorResponse
from typing import Dict, Any, List
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

@router.post("")
async def forecast_bed_occupancy(request: PredictionRequest) -> Dict[str, Any]:
    """
    Forecast hospital bed occupancy for a given ward and time period using a trained XGBoost model.
    """
    try:
        if xgb_model is None:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "MODEL_NOT_LOADED",
                    "error_message": "Prediction model is not available",
                    "details": {}
                }
            )

        # Prepare features for prediction
        features = []
        for i in range(request.days_ahead):
            features.append({
                "feature1": request.current_occupied_beds,
                "feature2": i + 1
            })
            
        # Make predictions
        X_pred = pd.DataFrame(features)
        y_pred = xgb_model.predict(X_pred)
        
        # Format predictions with proper date serialization
        predictions = []
        for i, pred in enumerate(y_pred):
            pred_date = (request.record_date + timedelta(days=i+1)).isoformat()
            predictions.append({
                "prediction_date": pred_date,
                "predicted_occupied_beds": float(pred),
                "confidence_lower": None,
                "confidence_upper": None,
                "confidence_score": None,
                "occupancy_rate": min(1.0, float(pred) / request.bed_count)
            })

        # Prepare response
        return {
            "success": True,
            "message": "Forecast generated successfully",
            "data": {
                "request_id": str(uuid4()),
                "hospital_id": request.hospital_id,
                "ward_id": request.ward_id,
                "model_id": request.model_id or "xgb_model_latest",
                "model_type": "xgboost",
                "base_date": request.record_date.isoformat(),
                "forecast_horizon_days": request.days_ahead,
                "predictions": predictions,
                "created_at": datetime.now().isoformat(),
                "metadata": {"note": "Prediction from trained XGBoost model."}
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "PREDICTION_ERROR",
                "error_message": str(e),
                "details": {}
            }
        )