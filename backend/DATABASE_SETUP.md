# Database Setup Guide

This project now supports both SQLite and MongoDB databases with easy switching between them. Here's how to set up and use each database option.

## Quick Start

### 1. Choose Your Database

**For Development (Recommended):** Use SQLite - no external database required
**For Production:** Use MongoDB - better scalability and performance

### 2. Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` file to set your preferred database:

#### SQLite Configuration (Default)
```env
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=hospital_bed_forecasting.db
```

#### MongoDB Configuration
```env
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=hospital_bed_forecasting
```

## Database Options

### SQLite (Built-in Database)

**Pros:**
- No external database setup required
- File-based storage - easy to backup and manage
- Perfect for development and testing
- Zero configuration

**Cons:**
- Limited scalability
- Not suitable for high-concurrency applications
- Fewer advanced features compared to MongoDB

**Setup:**
1. Set `DATABASE_TYPE=sqlite` in your `.env` file
2. Install dependencies: `pip install -r infra/requirements.txt`
3. Run the application: `python main.py`
4. SQLite database file will be created automatically

### MongoDB

**Pros:**
- Excellent scalability and performance
- Rich query capabilities
- Better for production environments
- Advanced features like aggregation, indexing

**Cons:**
- Requires external MongoDB setup
- More complex configuration
- Additional resource requirements

**Setup:**
1. Install MongoDB locally or use a cloud service (MongoDB Atlas)
2. Set `DATABASE_TYPE=mongodb` in your `.env` file
3. Configure MongoDB connection string in `.env`
4. Install dependencies: `pip install -r infra/requirements.txt`
5. Run the application: `python main.py`

## API Usage Examples

The API endpoints work the same regardless of which database you're using:

### 1. Create a Bed Occupancy Record
```bash
curl -X POST "http://localhost:8000/occupancy/" \
     -H "Content-Type: application/json" \
     -d '{
       "hospital_id": "hosp_001",
       "ward_id": "icu_1",
       "bed_count": 20,
       "occupied_beds": 15,
       "record_date": "2025-09-26T00:00:00"
     }'
```

### 2. Get All Records for a Hospital/Ward
```bash
curl "http://localhost:8000/occupancy/?hospital_id=hosp_001&ward_id=icu_1"
```

### 3. Get Records with Date Range
```bash
curl "http://localhost:8000/occupancy/?hospital_id=hosp_001&ward_id=icu_1&start_date=2025-09-01&end_date=2025-09-30"
```

### 4. Get Database Statistics
```bash
curl "http://localhost:8000/health/db"
```

### 5. Check Database Health
```bash
curl "http://localhost:8000/health/info"
```

## Switching Between Databases

### From SQLite to MongoDB
1. Stop the application
2. Change `DATABASE_TYPE` to `mongodb` in `.env`
3. Add MongoDB connection details
4. Start the application - it will automatically connect to MongoDB

### From MongoDB to SQLite
1. Stop the application
2. Change `DATABASE_TYPE` to `sqlite` in `.env`
3. Start the application - it will automatically create and use SQLite

## Database Migration

If you need to migrate data from SQLite to MongoDB:

1. Export data from SQLite using the API:
   ```bash
   curl "http://localhost:8000/occupancy/all" > sqlite_data.json
   ```

2. Switch to MongoDB in your `.env` file

3. Import data into MongoDB using the API:
   ```bash
   # Import each record from the JSON file
   # (You'll need to write a simple script for this)
   ```

## Testing

### Test with SQLite
```bash
# Set environment variable for testing
export DATABASE_TYPE=sqlite

# Run the application
python main.py

# Test API endpoints
curl "http://localhost:8000/health/db"
```

### Test with MongoDB
```bash
# Set environment variable for testing
export DATABASE_TYPE=mongodb

# Make sure MongoDB is running
mongod --dbpath /path/to/your/db

# Run the application
python main.py

# Test API endpoints
curl "http://localhost:8000/health/db"
```

## Troubleshooting

### SQLite Issues
- **Permission denied**: Make sure the application has write permissions in the directory
- **Database locked**: Only one application instance can write to SQLite at a time
- **File not found**: The database file will be created automatically on first run

### MongoDB Issues
- **Connection refused**: Make sure MongoDB is running and accessible
- **Authentication failed**: Check your MongoDB connection string and credentials
- **Database not found**: The database will be created automatically on first write operation

## Architecture Overview

The database abstraction layer consists of:

1. **DatabaseInterface** (`services/db/base.py`) - Abstract base class defining the contract
2. **SQLiteAdapter** (`services/db/sqlite_adapter.py`) - SQLite implementation
3. **MongoDBAdapter** (`services/db/mongodb_adapter.py`) - MongoDB implementation
4. **DatabaseFactory** (`services/db/factory.py`) - Factory pattern for database selection
5. **Database Services** (`services/db/sqlite.py`, `services/db/mongodb.py`) - Low-level database operations

This architecture allows you to:
- Switch databases by changing one environment variable
- Add new database types easily
- Maintain consistent API regardless of database backend
- Test with different databases without code changes
