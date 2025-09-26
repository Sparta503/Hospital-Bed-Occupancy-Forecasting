import sqlite3
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import aiosqlite
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SQLiteSettings(BaseSettings):
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "hospital_bed_forecasting.db")

sqlite_settings = SQLiteSettings()

class SQLiteDatabase:
    db_path: str = sqlite_settings.SQLITE_DB_PATH
    
    @classmethod
    async def initialize_db(cls):
        """Initialize SQLite database with required tables"""
        async with aiosqlite.connect(cls.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bed_occupancy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hospital_id TEXT NOT NULL,
                    ward_id TEXT NOT NULL,
                    bed_count INTEGER NOT NULL,
                    occupied_beds INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    record_date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_hospital_ward_date 
                ON bed_occupancy(hospital_id, ward_id, record_date)
            ''')
            
            await db.commit()
            print(f"SQLite database initialized at: {cls.db_path}")

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """Get database connection context manager"""
        async with aiosqlite.connect(cls.db_path) as db:
            db.row_factory = aiosqlite.Row  # Enable dictionary-like access
            yield db

    @classmethod
    async def insert_occupancy(cls, data: Dict[str, Any]) -> int:
        """Insert bed occupancy record and return the ID"""
        async with cls.get_connection() as db:
            cursor = await db.execute('''
                INSERT INTO bed_occupancy 
                (hospital_id, ward_id, bed_count, occupied_beds, timestamp, record_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['hospital_id'],
                data['ward_id'],
                data['bed_count'],
                data['occupied_beds'],
                data['timestamp'],
                data['record_date']
            ))
            await db.commit()
            return cursor.lastrowid

    @classmethod
    async def get_occupancy_by_id(cls, record_id: int) -> Optional[Dict[str, Any]]:
        """Get bed occupancy record by ID"""
        async with cls.get_connection() as db:
            cursor = await db.execute('''
                SELECT * FROM bed_occupancy WHERE id = ?
            ''', (record_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    @classmethod
    async def get_occupancy_by_hospital_ward(
        cls, 
        hospital_id: str, 
        ward_id: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get bed occupancy records by hospital and ward, optionally filtered by date range"""
        async with cls.get_connection() as db:
            query = '''
                SELECT * FROM bed_occupancy 
                WHERE hospital_id = ? AND ward_id = ?
            '''
            params = [hospital_id, ward_id]
            
            if start_date:
                query += ' AND record_date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND record_date <= ?'
                params.append(end_date)
            
            query += ' ORDER BY record_date DESC'
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @classmethod
    async def get_all_occupancy(cls) -> List[Dict[str, Any]]:
        """Get all bed occupancy records"""
        async with cls.get_connection() as db:
            cursor = await db.execute('SELECT * FROM bed_occupancy ORDER BY record_date DESC')
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @classmethod
    async def update_occupancy(cls, record_id: int, data: Dict[str, Any]) -> bool:
        """Update bed occupancy record"""
        async with cls.get_connection() as db:
            await db.execute('''
                UPDATE bed_occupancy 
                SET hospital_id = ?, ward_id = ?, bed_count = ?, 
                    occupied_beds = ?, timestamp = ?, record_date = ?
                WHERE id = ?
            ''', (
                data['hospital_id'],
                data['ward_id'],
                data['bed_count'],
                data['occupied_beds'],
                data['timestamp'],
                data['record_date'],
                record_id
            ))
            await db.commit()
            return True

    @classmethod
    async def delete_occupancy(cls, record_id: int) -> bool:
        """Delete bed occupancy record"""
        async with cls.get_connection() as db:
            await db.execute('DELETE FROM bed_occupancy WHERE id = ?', (record_id,))
            await db.commit()
            return True

    @classmethod
    async def get_occupancy_stats(cls) -> Dict[str, Any]:
        """Get basic statistics about bed occupancy data"""
        async with cls.get_connection() as db:
            cursor = await db.execute('''
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT hospital_id) as unique_hospitals,
                    COUNT(DISTINCT ward_id) as unique_wards,
                    AVG(occupied_beds) as avg_occupied_beds,
                    AVG(bed_count) as avg_total_beds
                FROM bed_occupancy
            ''')
            row = await cursor.fetchone()
            return dict(row) if row else {}
