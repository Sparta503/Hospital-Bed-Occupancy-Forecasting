import os
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
from services.etl.extract import extract_occupancy_data_from_csv
from services.etl.transform import transform_occupancy_data
from services.etl.load import load_occupancy_records
from services.etl.pipeline import run_etl_pipeline

# Path to the actual occupancy data
OCCUPANCY_CSV = Path(__file__).parent.parent / "services" / "etl" / "occupancy_data.csv"

# Check if the file exists
if not OCCUPANCY_CSV.exists():
    raise FileNotFoundError(f"Occupancy data file not found at {OCCUPANCY_CSV}. Please generate it first.")

# Test extract module
def test_extract_occupancy_data():
    """Test that data can be extracted from the CSV file."""
    records = extract_occupancy_data_from_csv(str(OCCUPANCY_CSV))
    
    # Check that we got data back
    assert len(records) > 0
    
    # Check that all expected fields are present
    expected_fields = {'hospital_id', 'ward_id', 'record_date', 'occupied_beds'}
    assert all(field in records[0] for field in expected_fields), \
        f"Missing fields. Expected: {expected_fields}, Found: {set(records[0].keys())}"

# Test transform module
def test_transform_occupancy_data():
    """Test that data is transformed correctly."""
    # First extract the data
    raw_records = extract_occupancy_data_from_csv(str(OCCUPANCY_CSV))
    
    # Transform the data
    transformed = transform_occupancy_data(raw_records)
    
    # Check that we got data back
    assert len(transformed) == len(raw_records)
    
    # Check that transformation was applied (is_weekend should be added)
    assert 'is_weekend' in transformed[0]
    
    # Check that occupied_beds is an integer
    assert isinstance(transformed[0]['occupied_beds'], int)

# Test load module
def test_load_occupancy_records():
    """Test that data can be loaded."""
    # Create test data
    test_data = [
        {'hospital_id': 1, 'ward_id': 'A', 'record_date': '2025-01-01', 'occupied_beds': 10},
        {'hospital_id': 1, 'ward_id': 'B', 'record_date': '2025-01-01', 'occupied_beds': 15}
    ]
    
    # Load the data
    count = load_occupancy_records(test_data)
    
    # Check that the correct number of records were processed
    assert count == len(test_data)

# Test the complete ETL pipeline
def test_etl_pipeline(tmp_path, monkeypatch):
    """Test the complete ETL pipeline."""
    # Create a temporary output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Mock the load_occupancy_records function to avoid actual database operations
    def mock_load(records):
        # Just return the count without doing anything
        return len(records)
    
    # Apply the mock
    import services.etl.load as load_module
    monkeypatch.setattr(load_module, 'load_occupancy_records', mock_load)
    
    # Run the ETL pipeline
    from services.etl.pipeline import run_etl_pipeline
    
    # Mock the extract_data function to use our test file
    def mock_extract():
        return extract_occupancy_data_from_csv(str(OCCUPANCY_CSV))
    
    # Apply the mock
    import services.etl.pipeline as pipeline_module
    monkeypatch.setattr(pipeline_module, 'extract_data', mock_extract)
    
    # Run the pipeline
    run_etl_pipeline()
    
    # If we get here without errors, the test passes
    assert True