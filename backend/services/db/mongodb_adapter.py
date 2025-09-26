from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import DatabaseInterface
from .mongodb import MongoDB
from services.models.occupancy import BedOccupancy

class MongoDBAdapter(DatabaseInterface):
    """MongoDB adapter implementing the DatabaseInterface"""
    
    async def initialize(self):
        """Initialize MongoDB connection"""
        await MongoDB.connect_db()
    
    async def close(self):
        """Close MongoDB connection"""
        await MongoDB.close_db()
    
    async def create_occupancy_record(self, data: Dict[str, Any]) -> str:
        """Create a new bed occupancy record"""
        # Convert string dates to datetime objects if needed
        if isinstance(data.get('record_date'), str):
            data['record_date'] = datetime.fromisoformat(data['record_date'].replace('Z', '+00:00'))
        
        occupancy = BedOccupancy(**data)
        await occupancy.insert()
        return str(occupancy.id)
    
    async def get_occupancy_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a bed occupancy record by ID"""
        try:
            occupancy = await BedOccupancy.get(record_id)
            if occupancy:
                return {
                    'id': str(occupancy.id),
                    'hospital_id': occupancy.hospital_id,
                    'ward_id': occupancy.ward_id,
                    'bed_count': occupancy.bed_count,
                    'occupied_beds': occupancy.occupied_beds,
                    'timestamp': occupancy.timestamp.isoformat(),
                    'record_date': occupancy.record_date.isoformat()
                }
            return None
        except Exception:
            return None
    
    async def get_occupancy_records(
        self, 
        hospital_id: str, 
        ward_id: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get bed occupancy records by hospital and ward"""
        query = {
            'hospital_id': hospital_id,
            'ward_id': ward_id
        }
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                date_query['$lte'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query['record_date'] = date_query
        
        records = await BedOccupancy.find(query).sort('-record_date').to_list()
        
        return [
            {
                'id': str(record.id),
                'hospital_id': record.hospital_id,
                'ward_id': record.ward_id,
                'bed_count': record.bed_count,
                'occupied_beds': record.occupied_beds,
                'timestamp': record.timestamp.isoformat(),
                'record_date': record.record_date.isoformat()
            }
            for record in records
        ]
    
    async def get_all_occupancy_records(self) -> List[Dict[str, Any]]:
        """Get all bed occupancy records"""
        records = await BedOccupancy.find_all().sort('-record_date').to_list()
        
        return [
            {
                'id': str(record.id),
                'hospital_id': record.hospital_id,
                'ward_id': record.ward_id,
                'bed_count': record.bed_count,
                'occupied_beds': record.occupied_beds,
                'timestamp': record.timestamp.isoformat(),
                'record_date': record.record_date.isoformat()
            }
            for record in records
        ]
    
    async def update_occupancy_record(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Update a bed occupancy record"""
        try:
            occupancy = await BedOccupancy.get(record_id)
            if occupancy:
                # Update fields
                for key, value in data.items():
                    if hasattr(occupancy, key):
                        if key in ['record_date', 'timestamp'] and isinstance(value, str):
                            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        setattr(occupancy, key, value)
                
                await occupancy.save()
                return True
            return False
        except Exception:
            return False
    
    async def delete_occupancy_record(self, record_id: str) -> bool:
        """Delete a bed occupancy record"""
        try:
            occupancy = await BedOccupancy.get(record_id)
            if occupancy:
                await occupancy.delete()
                return True
            return False
        except Exception:
            return False
    
    async def get_occupancy_statistics(self) -> Dict[str, Any]:
        """Get bed occupancy statistics"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_records': {'$sum': 1},
                    'unique_hospitals': {'$addToSet': '$hospital_id'},
                    'unique_wards': {'$addToSet': '$ward_id'},
                    'avg_occupied_beds': {'$avg': '$occupied_beds'},
                    'avg_total_beds': {'$avg': '$bed_count'}
                }
            }
        ]
        
        result = await BedOccupancy.aggregate(pipeline).to_list()
        
        if result:
            stats = result[0]
            return {
                'total_records': stats['total_records'],
                'unique_hospitals': len(stats['unique_hospitals']),
                'unique_wards': len(stats['unique_wards']),
                'avg_occupied_beds': stats['avg_occupied_beds'],
                'avg_total_beds': stats['avg_total_beds']
            }
        
        return {
            'total_records': 0,
            'unique_hospitals': 0,
            'unique_wards': 0,
            'avg_occupied_beds': 0,
            'avg_total_beds': 0
        }
