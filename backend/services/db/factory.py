from typing import Union
from .base import DatabaseInterface
from .sqlite_adapter import SQLiteAdapter
from .mongodb_adapter import MongoDBAdapter
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseSettings(BaseSettings):
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")  # "sqlite" or "mongodb"

db_settings = DatabaseSettings()

class DatabaseFactory:
    """Factory class to create database instances based on configuration"""
    
    @staticmethod
    def create_database() -> DatabaseInterface:
        """Create and return the appropriate database instance"""
        if db_settings.DATABASE_TYPE.lower() == "mongodb":
            return MongoDBAdapter()
        elif db_settings.DATABASE_TYPE.lower() == "sqlite":
            return SQLiteAdapter()
        else:
            raise ValueError(f"Unsupported database type: {db_settings.DATABASE_TYPE}")
    
    @staticmethod
    def get_database_type() -> str:
        """Get the current database type"""
        return db_settings.DATABASE_TYPE.lower()

# Global database instance
_db_instance: Union[DatabaseInterface, None] = None

async def get_database() -> DatabaseInterface:
    """Get or create the database instance (singleton pattern)"""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseFactory.create_database()
        await _db_instance.initialize()
    
    return _db_instance

async def close_database():
    """Close the database connection"""
    global _db_instance
    
    if _db_instance:
        await _db_instance.close()
        _db_instance = None

def switch_database(database_type: str):
    """Switch to a different database type"""
    global _db_instance
    
    if database_type.lower() not in ["sqlite", "mongodb"]:
        raise ValueError("Database type must be either 'sqlite' or 'mongodb'")
    
    # Close existing connection if any
    if _db_instance:
        # Note: This should be called in an async context
        # For now, we'll just set to None and let the next get_database() handle initialization
        _db_instance = None
    
    # Update environment variable
    os.environ["DATABASE_TYPE"] = database_type.lower()
