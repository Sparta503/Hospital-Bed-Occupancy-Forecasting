from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from services.db.factory import get_database

router = APIRouter()

# Pydantic models for request/response
class BedOccupancyCreate(BaseModel):
    hospital_id: str
    ward_id: str
    bed_count: int
    occupied_beds: int
    record_date: str

class BedOccupancyResponse(BaseModel):
    id: str
    hospital_id: str
    ward_id: str
    bed_count: int
    occupied_beds: int
    timestamp: str
    record_date: str

class BedOccupancyStats(BaseModel):
    total_records: int
    unique_hospitals: int
    unique_wards: int
    avg_occupied_beds: float
    avg_total_beds: float

@router.post("/occupancy/", response_model=BedOccupancyResponse)
async def create_occupancy_record(
    occupancy_data: BedOccupancyCreate,
    db=Depends(get_database)
):
    """Create a new bed occupancy record"""
    try:
        # Prepare data for database
        data = {
            "hospital_id": occupancy_data.hospital_id,
            "ward_id": occupancy_data.ward_id,
            "bed_count": occupancy_data.bed_count,
            "occupied_beds": occupancy_data.occupied_beds,
            "timestamp": datetime.utcnow().isoformat(),
            "record_date": occupancy_data.record_date
        }
        
        # Validate that occupied_beds <= bed_count
        if occupancy_data.occupied_beds > occupancy_data.bed_count:
            raise HTTPException(
                status_code=400, 
                detail="Occupied beds cannot exceed total bed count"
            )
        
        record_id = await db.create_occupancy_record(data)
        
        # Return the created record
        created_record = await db.get_occupancy_record(record_id)
        if not created_record:
            raise HTTPException(status_code=500, detail="Failed to create record")
        
        return BedOccupancyResponse(**created_record)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")

@router.get("/occupancy/{record_id}", response_model=BedOccupancyResponse)
async def get_occupancy_record(
    record_id: str,
    db=Depends(get_database)
):
    """Get a specific bed occupancy record by ID"""
    try:
        record = await db.get_occupancy_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return BedOccupancyResponse(**record)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving record: {str(e)}")

@router.get("/occupancy/", response_model=List[BedOccupancyResponse])
async def get_occupancy_records(
    hospital_id: str,
    ward_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db=Depends(get_database)
):
    """Get bed occupancy records for a specific hospital and ward"""
    try:
        records = await db.get_occupancy_records(
            hospital_id=hospital_id,
            ward_id=ward_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return [BedOccupancyResponse(**record) for record in records]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving records: {str(e)}")

@router.get("/occupancy/all", response_model=List[BedOccupancyResponse])
async def get_all_occupancy_records(db=Depends(get_database)):
    """Get all bed occupancy records"""
    try:
        records = await db.get_all_occupancy_records()
        return [BedOccupancyResponse(**record) for record in records]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving records: {str(e)}")

@router.put("/occupancy/{record_id}", response_model=BedOccupancyResponse)
async def update_occupancy_record(
    record_id: str,
    occupancy_data: BedOccupancyCreate,
    db=Depends(get_database)
):
    """Update a bed occupancy record"""
    try:
        # Check if record exists
        existing_record = await db.get_occupancy_record(record_id)
        if not existing_record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Validate that occupied_beds <= bed_count
        if occupancy_data.occupied_beds > occupancy_data.bed_count:
            raise HTTPException(
                status_code=400, 
                detail="Occupied beds cannot exceed total bed count"
            )
        
        # Prepare update data
        update_data = {
            "hospital_id": occupancy_data.hospital_id,
            "ward_id": occupancy_data.ward_id,
            "bed_count": occupancy_data.bed_count,
            "occupied_beds": occupancy_data.occupied_beds,
            "timestamp": datetime.utcnow().isoformat(),
            "record_date": occupancy_data.record_date
        }
        
        success = await db.update_occupancy_record(record_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update record")
        
        # Return updated record
        updated_record = await db.get_occupancy_record(record_id)
        return BedOccupancyResponse(**updated_record)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating record: {str(e)}")

@router.delete("/occupancy/{record_id}")
async def delete_occupancy_record(
    record_id: str,
    db=Depends(get_database)
):
    """Delete a bed occupancy record"""
    try:
        # Check if record exists
        existing_record = await db.get_occupancy_record(record_id)
        if not existing_record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        success = await db.delete_occupancy_record(record_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete record")
        
        return {"message": "Record deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting record: {str(e)}")

@router.get("/occupancy/stats", response_model=BedOccupancyStats)
async def get_occupancy_statistics(db=Depends(get_database)):
    """Get bed occupancy statistics"""
    try:
        stats = await db.get_occupancy_statistics()
        return BedOccupancyStats(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
