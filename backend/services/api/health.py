from fastapi import APIRouter, Depends, HTTPException
from services.db.mongodb import get_database, MongoDB
from motor.motor_asyncio import AsyncIOMotorDatabase
from beanie.odm.documents import Document

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
async def check_db_connection():
    """Check database connection and return status"""
    try:
        db = await get_database()
        # Ping the database to check connection
        await db.command("ping")
        return {"status": "connected", "database": db.name}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

@router.get("/collections")
async def list_collections():
    """List all collections in the database"""
    try:
        if not MongoDB.db:
            await MongoDB.connect_db()
        collections = await MongoDB.db.list_collection_names()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list collections: {str(e)}"
        )
