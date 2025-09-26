from fastapi import APIRouter, Depends, HTTPException
from services.db.factory import get_database, DatabaseFactory
from services.db.base import DatabaseInterface

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)

@router.get("/status")
async def health_check():
    """Check if the API is running"""
    return {"status": "ok"}

@router.get("/db")
async def check_db_connection(db: DatabaseInterface = Depends(get_database)):
    """Check database connection and return status"""
    try:
        # Test database connection by getting statistics
        stats = await db.get_occupancy_statistics()
        return {
            "status": "connected", 
            "database_type": DatabaseFactory.get_database_type(),
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

@router.get("/info")
async def get_database_info(db: DatabaseInterface = Depends(get_database)):
    """Get database information and status"""
    try:
        stats = await db.get_occupancy_statistics()
        return {
            "database_type": DatabaseFactory.get_database_type(),
            "status": "connected",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database info: {str(e)}"
        )
