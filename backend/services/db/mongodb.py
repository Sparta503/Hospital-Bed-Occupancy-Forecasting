from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "hospital_bed_forecasting")

settings = Settings()

# Database connection
class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.MONGODB_DB_NAME]
        
        # Initialize Beanie with your document models
        from services.models.occupancy import BedOccupancy
        await init_beanie(database=cls.db, document_models=[BedOccupancy])
        print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            print("Closed MongoDB connection")

# Dependency to get database instance
async def get_database():
    if not MongoDB.db:
        await MongoDB.connect_db()
    return MongoDB.db
