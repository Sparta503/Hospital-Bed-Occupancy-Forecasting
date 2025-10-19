"""
Pytest configuration and fixtures for testing the Hospital Bed Occupancy Forecasting API.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import random
import string

from services.api.main import app

@pytest.fixture(scope="module")
def test_client():
    """Fixture that provides a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_occupancy_data():
    """Fixture that provides sample occupancy data for testing."""
    return {
        "hospital_id": "TEST" + ''.join(random.choices(string.digits, k=3)),
        "ward_id": "WARD" + ''.join(random.choices(string.digits, k=2)),
        "ward_type": random.choice(["icu", "emergency", "general"]),
        "bed_count": random.randint(10, 100),
        "occupied_beds": random.randint(0, 50),
        "record_date": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat()
    }

@pytest.fixture
def sample_forecast_request():
    """Fixture that provides sample forecast request data for testing."""
    return {
        "hospital_id": "TEST" + ''.join(random.choices(string.digits, k=3)),
        "ward_id": "WARD" + ''.join(random.choices(string.digits, k=2)),
        "ward_type": random.choice(["icu", "emergency", "general"]),
        "bed_count": random.randint(10, 100),
        "current_occupied_beds": random.randint(0, 50),
        "record_date": datetime.utcnow().isoformat(),
        "days_ahead": random.choice([1, 3, 7, 14]),
        "model_id": f"model_{random.choice(['v1', 'v2', 'v3'])}",
        "include_confidence": random.choice([True, False])
    }

@pytest.fixture
def auth_headers():
    """Fixture that provides authentication headers for testing protected endpoints."""
    # In a real application, this would generate a valid JWT or API key
    return {
        "Authorization": f"Bearer test_token_{random.randint(1000, 9999)}",
        "Content-Type": "application/json"
    }