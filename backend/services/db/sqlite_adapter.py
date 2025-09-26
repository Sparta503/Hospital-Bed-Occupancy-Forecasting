from typing import List, Dict, Any, Optional
from .base import DatabaseInterface
from .sqlite import SQLiteDatabase

class SQLiteAdapter(DatabaseInterface):
    """SQLite adapter implementing the DatabaseInterface"""
    
    async def initialize(self):
        """Initialize SQLite database"""
        await SQLiteDatabase.initialize_db()
    
    async def close(self):
        """Close SQLite database connection (handled automatically by aiosqlite)"""
        pass
    
    async def create_occupancy_record(self, data: Dict[str, Any]) -> str:
        """Create a new bed occupancy record"""
        record_id = await SQLiteDatabase.insert_occupancy(data)
        return str(record_id)
    
    async def get_occupancy_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a bed occupancy record by ID"""
        try:
            return await SQLiteDatabase.get_occupancy_by_id(int(record_id))
        except (ValueError, TypeError):
            return None
    
    async def get_occupancy_records(
        self, 
        hospital_id: str, 
        ward_id: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get bed occupancy records by hospital and ward"""
        return await SQLiteDatabase.get_occupancy_by_hospital_ward(
            hospital_id, ward_id, start_date, end_date
        )
    
    async def get_all_occupancy_records(self) -> List[Dict[str, Any]]:
        """Get all bed occupancy records"""
        return await SQLiteDatabase.get_all_occupancy()
    
    async def update_occupancy_record(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Update a bed occupancy record"""
        try:
            return await SQLiteDatabase.update_occupancy(int(record_id), data)
        except (ValueError, TypeError):
            return False
    
    async def delete_occupancy_record(self, record_id: str) -> bool:
        """Delete a bed occupancy record"""
        try:
            return await SQLiteDatabase.delete_occupancy(int(record_id))
        except (ValueError, TypeError):
            return False
    
    async def get_occupancy_statistics(self) -> Dict[str, Any]:
        """Get bed occupancy statistics"""
        return await SQLiteDatabase.get_occupancy_stats()
