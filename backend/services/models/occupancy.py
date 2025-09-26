from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field

class BedOccupancy(Document):
    """
    Model for storing hospital bed occupancy data
    """
    hospital_id: str = Field(..., description="Unique identifier for the hospital")
    ward_id: str = Field(..., description="Ward or department identifier")
    bed_count: int = Field(..., description="Total number of beds in the ward")
    occupied_beds: int = Field(..., description="Number of occupied beds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this record was created")
    record_date: Indexed(datetime) = Field(..., description="The date this occupancy record is for")
    
    class Settings:
        name = "bed_occupancy"
        indexes = [
            [("hospital_id", 1), ("ward_id", 1), ("record_date", -1)],  # Compound index for common queries
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "hospital_id": "hosp_123",
                "ward_id": "icu_1",
                "bed_count": 20,
                "occupied_beds": 15,
                "record_date": "2025-09-08T00:00:00"
            }
        }
