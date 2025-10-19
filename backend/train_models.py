"""
Model Training Script for Hospital Bed Occupancy Forecasting

This script trains and evaluates both XGBoost and Prophet models
for hospital bed occupancy forecasting.
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import joblib
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MODEL_DIR = Path("models")
DATA_DIR = Path("data")
CONFIG_DIR = Path("config")

# Ensure directories exist
MODEL_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# Default model parameters
DEFAULT_XGB_PARAMS = {
    'objective': 'reg:squarederror',
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}

DEFAULT_PROPHET_PARAMS = {
    'changepoint_prior_scale': 0.05,
    'seasonality_prior_scale': 10.0,
    'holidays_prior_scale': 10.0,
    'seasonality_mode': 'multiplicative',
    'weekly_seasonality': True,
    'daily_seasonality': False,
    'yearly_seasonality': True
}

def load_training_data(file_path: str) -> pd.DataFrame:
    """Load and preprocess training data."""
    logger.info(f"Loading training data from {file_path}")
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Basic validation
        required_columns = ['record_date', 'ward_id', 'occupied_beds', 'hospital_id']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Add total_beds if not present (using a default of 50, adjust as needed)
        if 'total_beds' not in df.columns:
            logger.warning("total_beds column not found. Using default value of 50.")
            df['total_beds'] = 50
        
        # Convert date column to datetime and rename to 'date' for consistency
        df['date'] = pd.to_datetime(df['record_date'])
        
        # Sort by date
        df = df.sort_values('date')
        
        # Calculate occupancy rate
        df['occupancy_rate'] = df['occupied_beds'] / df['total_beds']
        
        # Add time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        # Add ward_type if not present (using a default of 'general')
        if 'ward_type' not in df.columns:
            logger.warning("ward_type column not found. Using default value of 'general'.")
            df['ward_type'] = 'general'
        
        logger.info(f"Successfully loaded {len(df)} records")
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
        logger.info(f"Wards: {df['ward_id'].nunique()}")
        logger.info(f"Hospitals: {df['hospital_id'].nunique()}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error loading training data: {str(e)}")
        raise

def train_xgb_model(train_data: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> tuple:
    """Train an XGBoost model."""
    from xgboost import XGBRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    
    logger.info("Training XGBoost model")
    
    # Use default params if none provided
    if params is None:
        params = DEFAULT_XGB_PARAMS
    
    try:
        # Prepare features and target
        features = ['day_of_week', 'month', 'year', 'total_beds']
        X = train_data[features]
        y = train_data['occupied_beds']
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Train model
        model = XGBRegressor(**params)
        
        # Set eval_metric in params if not already set
        if 'eval_metric' not in params:
            model.set_params(eval_metric='mae')
            
        model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_val, y_val)],
            verbose=10
        )
        
        # Evaluate
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        
        logger.info(f"XGBoost training complete. MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        
        return model, {"mae": mae, "rmse": rmse}
        
    except Exception as e:
        logger.error(f"Error training XGBoost model: {str(e)}")
        raise

def train_prophet_model(train_data: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> tuple:
    """Train a Prophet model."""
    from prophet import Prophet
    from prophet.diagnostics import cross_validation, performance_metrics
    
    logger.info("Training Prophet model")
    
    # Use default params if none provided
    if params is None:
        params = DEFAULT_PROPHET_PARAMS
    
    try:
        # Prepare data for Prophet
        df_prophet = train_data[['date', 'occupied_beds']].copy()
        df_prophet = df_prophet.rename(columns={'date': 'ds', 'occupied_beds': 'y'})
        
        # Add additional regressors
        for col in ['day_of_week', 'month', 'year', 'total_beds']:
            df_prophet[col] = train_data[col].values
        
        # Initialize and fit model
        model = Prophet(**params)
        
        # Add additional regressors
        for col in ['day_of_week', 'month', 'year', 'total_beds']:
            model.add_regressor(col)
        
        model.fit(df_prophet)
        
        # Cross-validation
        df_cv = cross_validation(
            model,
            initial='365 days',
            period='30 days',
            horizon='30 days'
        )
        
        # Calculate metrics
        df_p = performance_metrics(df_cv)
        mae = df_p['mae'].mean()
        rmse = df_p['rmse'].mean()
        
        logger.info(f"Prophet training complete. MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        
        return model, {"mae": mae, "rmse": rmse}
        
    except Exception as e:
        logger.error(f"Error training Prophet model: {str(e)}")
        raise

def save_model(model, model_name: str, metrics: Dict[str, float], model_type: str):
    """Save the trained model and its metadata."""
    try:
        # Create model directory
        model_dir = MODEL_DIR / model_type.lower()
        model_dir.mkdir(exist_ok=True)
        
        # Generate model filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{model_name}_{timestamp}.joblib"
        model_path = model_dir / model_filename
        
        # Save model
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata = {
            "model_name": model_name,
            "model_type": model_type,
            "training_date": datetime.now().isoformat(),
            "metrics": metrics,
            "model_path": str(model_path.absolute())
        }
        
        metadata_path = model_dir / f"{model_name}_{timestamp}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to {model_path}")
        return str(model_path)
        
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise

def generate_sample_data(num_days: int = 365) -> pd.DataFrame:
    """Generate sample training data for demonstration purposes."""
    logger.info(f"Generating {num_days} days of sample data")
    
    # Generate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Generate sample data for 3 wards
    wards = ['WARD1', 'WARD2', 'WARD3']
    total_beds = {'WARD1': 50, 'WARD2': 30, 'WARD3': 40}
    
    data = []
    for ward in wards:
        # Generate base occupancy with weekly seasonality
        base_occupancy = np.sin(np.linspace(0, num_days/7, num_days) * 2 * np.pi) * 0.3 + 0.5
        # Add some random noise
        noise = np.random.normal(0, 0.1, num_days)
        occupancy_rates = np.clip(base_occupancy + noise, 0, 0.9)  # Cap at 90% occupancy
        
        for i, date in enumerate(dates):
            # Use modulo to wrap around the index if it exceeds the array length
            idx = i % num_days
            occupied = int(occupancy_rates[idx] * total_beds[ward])
            data.append({
                'date': date,
                'ward_id': ward,
                'total_beds': total_beds[ward],
                'occupied_beds': occupied,
                'admissions': np.random.poisson(3),  # Simulate daily admissions
                'discharges': np.random.poisson(3)   # Simulate daily discharges
            })
    
    df = pd.DataFrame(data)
    
    # Add time-based features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    
    # Add record_date for compatibility with load_training_data
    df['record_date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # Add hospital_id with default value if not present
    if 'hospital_id' not in df.columns:
        df['hospital_id'] = 'HOSP1'  # Default hospital ID
    
    # Add ward_type with default value if not present
    if 'ward_type' not in df.columns:
        df['ward_type'] = 'general'
    
    # Save sample data
    sample_data_path = DATA_DIR / 'sample_training_data.csv'
    df.to_csv(sample_data_path, index=False)
    logger.info(f"Sample data saved to {sample_data_path}")
    logger.info(f"Generated columns: {df.columns.tolist()}")
    
    return df

def main():
    """Main training function."""
    try:
        # Check for training data
        data_file = DATA_DIR / 'training_data.csv'
        
        if not data_file.exists():
            logger.warning("No training data found. Generating sample data...")
            df = generate_sample_data()
        else:
            df = load_training_data(data_file)
        
        # Train XGBoost model
        xgb_model, xgb_metrics = train_xgb_model(df)
        save_model(xgb_model, "bed_occupancy_xgb", xgb_metrics, "xgb")
        
        # Train Prophet model
        prophet_model, prophet_metrics = train_prophet_model(df)
        save_model(prophet_model, "bed_occupancy_prophet", prophet_metrics, "prophet")
        
        logger.info("Model training completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        raise

if __name__ == "__main__":
    main()
