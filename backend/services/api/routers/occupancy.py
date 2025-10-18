from fastapi import APIRouter, HTTPException
from ..schemas import BedOccupancyInput, ApiResponse, ErrorResponse
from typing import Any
from uuid import uuid4
from datetime import datetime

router = APIRouter()

@router.post("/occupancy")
async def add_occupancy_record(record: BedOccupancyInput) -> dict:
    """
    Ingest a new hospital bed occupancy record.
    """
    try:
        # Dummy logic: In production, save to DB
        return {
            "success": True,
            "message": "Occupancy record ingested successfully.",
            "data": {
                "record_id": str(uuid4()),
                "received": record.model_dump(),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_RECORD",
                "error_message": str(e),
                "details": {}
            }
        )