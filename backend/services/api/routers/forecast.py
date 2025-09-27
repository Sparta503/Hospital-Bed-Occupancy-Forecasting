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
    try:
        predictions = []
        for i in range(request.days_ahead):
            pred_date = request.record_date + timedelta(days=i+1)
            predictions.append({
                "prediction_date": pred_date,
                "predicted_occupied_beds": max(0, request.current_occupied_beds - i),
                "confidence_lower": None,
                "confidence_upper": None,
                "confidence_score": 0.9,
                "occupancy_rate": min(1.0, (request.current_occupied_beds - i) / request.bed_count)
            })
        response = ForecastResponse(
            request_id=str(uuid4()),
            hospital_id=request.hospital_id,
            ward_id=request.ward_id,
            model_id=request.model_id or "dummy-model-id",
            model_type="xgboost",
            base_date=request.record_date,
            forecast_horizon_days=request.days_ahead,
            predictions=predictions,
            created_at=datetime.now(),
            metadata={"note": "This is a dummy forecast. Replace with real model."}
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))