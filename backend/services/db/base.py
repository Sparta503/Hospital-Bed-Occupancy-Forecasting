from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseInterface(ABC):
    """Abstract base class for database implementations"""
    
    @abstractmethod
    async def initialize(self):
        """Initialize the database connection and schema"""
        pass
    
    @abstractmethod
    async def close(self):
        """Close the database connection"""
        pass
    
    @abstractmethod
    async def create_occupancy_record(self, data: Dict[str, Any]) -> str:
        """Create a new bed occupancy record"""
        pass
    
    @abstractmethod
    async def get_occupancy_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a bed occupancy record by ID"""
        pass
    
    @abstractmethod
    async def get_occupancy_records(
        self, 
        hospital_id: str, 
        ward_id: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get bed occupancy records by hospital and ward"""
        pass
    
    @abstractmethod
    async def get_all_occupancy_records(self) -> List[Dict[str, Any]]:
        """Get all bed occupancy records"""
        pass
    
    @abstractmethod
    async def update_occupancy_record(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Update a bed occupancy record"""
        pass
    
    @abstractmethod
    async def delete_occupancy_record(self, record_id: str) -> bool:
        """Delete a bed occupancy record"""
        pass
    
    @abstractmethod
    async def get_occupancy_statistics(self) -> Dict[str, Any]:
        """Get bed occupancy statistics"""
        pass
