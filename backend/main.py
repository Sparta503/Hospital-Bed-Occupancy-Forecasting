from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.db.mongodb import MongoDB
import uvicorn
from contextlib import asynccontextmanager
from services.api import health

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await MongoDB.connect_db()
    yield
    # Shutdown: Close MongoDB connection
    await MongoDB.close_db()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "Hospital Bed Occupancy Forecasting API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
