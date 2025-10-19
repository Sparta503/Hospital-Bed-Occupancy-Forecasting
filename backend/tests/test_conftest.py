"""
Tests for the fixtures defined in conftest.py
"""
import pytest
from datetime import datetime


def test_test_client_fixture(test_client):
    """Test that the test_client fixture returns a working FastAPI test client."""
    # Test a simple endpoint (health check)
    response = test_client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_sample_occupancy_data_fixture(sample_occupancy_data):
    """Test the sample_occupancy_data fixture."""
    # Check required fields exist
    required_fields = [
        "hospital_id", "ward_id", "ward_type",
        "bed_count", "occupied_beds", "record_date"
    ]
    for field in required_fields:
        assert field in sample_occupancy_data
    
    # Check data types
    assert isinstance(sample_occupancy_data["hospital_id"], str)
    assert sample_occupancy_data["hospital_id"].startswith("TEST")
    assert sample_occupancy_data["ward_id"].startswith("WARD")
    assert sample_occupancy_data["ward_type"] in ["icu", "emergency", "general"]
    assert 10 <= sample_occupancy_data["bed_count"] <= 100
    assert 0 <= sample_occupancy_data["occupied_beds"] <= 50
    
    # Verify the date is in ISO format
    try:
        datetime.fromisoformat(sample_occupancy_data["record_date"])
    except ValueError:
        pytest.fail("record_date is not in valid ISO format")


def test_sample_forecast_request_fixture(sample_forecast_request):
    """Test the sample_forecast_request fixture."""
    # Check required fields exist
    required_fields = [
        "hospital_id", "ward_id", "ward_type", "bed_count",
        "current_occupied_beds", "record_date", "days_ahead",
        "model_id", "include_confidence"
    ]
    for field in required_fields:
        assert field in sample_forecast_request
    
    # Check data types and values
    assert sample_forecast_request["hospital_id"].startswith("TEST")
    assert sample_forecast_request["ward_id"].startswith("WARD")
    assert sample_forecast_request["ward_type"] in ["icu", "emergency", "general"]
    assert 10 <= sample_forecast_request["bed_count"] <= 100
    assert 0 <= sample_forecast_request["current_occupied_beds"] <= 50
    assert sample_forecast_request["days_ahead"] in [1, 3, 7, 14]
    assert sample_forecast_request["model_id"].startswith("model_")
    assert isinstance(sample_forecast_request["include_confidence"], bool)
    
    # Verify the date is in ISO format
    try:
        datetime.fromisoformat(sample_forecast_request["record_date"])
    except ValueError:
        pytest.fail("record_date is not in valid ISO format")


def test_auth_headers_fixture(auth_headers):
    """Test the auth_headers fixture."""
    # Check required headers exist
    assert "Authorization" in auth_headers
    assert "Content-Type" in auth_headers
    
    # Check header values
    assert auth_headers["Authorization"].startswith("Bearer test_token_")
    assert auth_headers["Content-Type"] == "application/json"
    
    # Check the token format
    token = auth_headers["Authorization"].split("_")[-1]
    assert token.isdigit() and len(token) == 4
