"""
XGBoost Training Script for Hospital Bed Occupancy Forecasting

This module provides a function to train an XGBoost model on historical occupancy data.
Replace dummy data loading and file paths with real data and configuration as needed.
"""
import xgboost as xgb
import pandas as pd
import joblib
from typing import Optional, Dict, Any
from datetime import datetime
import os

# Main training function
def train_xgb_model(
    train_data: pd.DataFrame,
    target_column: str = "occupied_beds",
    model_save_path: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Train an XGBoost regressor and save the model to disk.
    Args:
        train_data: DataFrame containing features and target
        target_column: Name of the target variable
        model_save_path: Path to save the trained model (optional)
        params: XGBoost hyperparameters (optional)
    Returns:
        str: Path to the saved model file
    """
    if params is None:
        params = {
            "objective": "reg:squarederror",
            "max_depth": 5,
            "learning_rate": 0.1,
            "n_estimators": 100,
            "seed": 42
        }
    X = train_data.drop(columns=[target_column])
    y = train_data[target_column]
    model = xgb.XGBRegressor(**params)
    model.fit(X, y)
    if not model_save_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_save_path = f"xgb_model_{timestamp}.joblib"
    joblib.dump(model, model_save_path)
    return model_save_path

# Example usage (remove or adapt in production)
if __name__ == "__main__":
    import pandas as pd
    # Load data from generated CSV
    csv_file = "occupancy_data.csv"
    try:
        df = pd.read_csv(csv_file)
        # Use ward_id as a categorical feature (convert to codes), and record_date as days since first date
        df["ward_id_code"] = df["ward_id"].astype("category").cat.codes
        df["days_since_start"] = (pd.to_datetime(df["record_date"]) - pd.to_datetime(df["record_date"]).min()).dt.days
        feature_df = df[["ward_id_code", "days_since_start", "occupied_beds"]]
        model_path = train_xgb_model(feature_df, target_column="occupied_beds")
        print(f"Model saved to {model_path}")
    except FileNotFoundError:
        print(f"File {csv_file} not found. Please provide a valid CSV file.")