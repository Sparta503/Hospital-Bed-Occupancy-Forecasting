"""
Model Evaluation Script for Hospital Bed Occupancy Forecasting

This module provides functions to evaluate regression models (XGBoost, Prophet, etc.)
using common metrics such as RMSE, MAE, MAPE, and R2.
"""
import numpy as np
from typing import Sequence, Dict
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Optional: MAPE implementation (sklearn does not provide this by default)
def mean_absolute_percentage_error(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    nonzero = y_true != 0
    if not np.any(nonzero):
        return np.nan
    return np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100

def evaluate_regression(y_true: Sequence[float], y_pred: Sequence[float]) -> Dict[str, float]:
    """
    Evaluate regression predictions using standard metrics.
    Args:
        y_true: True target values
        y_pred: Predicted values
    Returns:
        Dict with RMSE, MAE, MAPE, and R2
    """
    return {
        "rmse": mean_squared_error(y_true, y_pred, squared=False),
        "mae": mean_absolute_error(y_true, y_pred),
        "mape": mean_absolute_percentage_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred)
    }

# Example usage (remove or adapt in production)
if __name__ == "__main__":
    import pandas as pd
    # Load data from generated CSV
    csv_file = "occupancy_data.csv"
    try:
        df = pd.read_csv(csv_file)
        y_true = df["occupied_beds"].tolist()
        # For demonstration, use the same as predictions (in practice, use your model's predictions)
        y_pred = y_true.copy()
        metrics = evaluate_regression(y_true, y_pred)
        print("Evaluation metrics on occupancy_data.csv:", metrics)
    except FileNotFoundError:
        print(f"File {csv_file} not found. Please provide a valid CSV file.")