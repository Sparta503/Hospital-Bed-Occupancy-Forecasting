from fastapi import APIRouter, HTTPException
from ..schemas import BedOccupancyInput, ApiResponse, ErrorResponse
from typing import Any
from uuid import uuid4
from datetime import datetime

router = APIRouter()

@router.post("/occupancy", response_model=ApiResponse, responses={400: {"model": ErrorResponse}})
async def add_occupancy_record(record: BedOccupancyInput) -> Any:
    """
    Ingest a new hospital bed occupancy record.
    """
    try:
        # Dummy logic: In production, save to DB
        return ApiResponse(
            success=True,
            message="Occupancy record ingested successfully.",
            data={
                "record_id": str(uuid4()),
                "received": record.dict(),
                "timestamp": datetime.now()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))