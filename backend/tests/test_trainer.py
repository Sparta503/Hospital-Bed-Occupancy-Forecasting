import os
import pandas as pd
from services.trainer.train_xgb import train_xgb_model
from services.trainer.train_prophet import train_prophet_model

def test_train_xgb_model(tmp_path):
    # Load data from generated CSV
    csv_path = "./services/etl/occupancy_data.csv"
    df = pd.read_csv(csv_path)
    # Create features for XGBoost
    df["ward_id_code"] = df["ward_id"].astype("category").cat.codes
    df["days_since_start"] = (pd.to_datetime(df["record_date"]) - pd.to_datetime(df["record_date"]).min()).dt.days
    feature_df = df[["ward_id_code", "days_since_start", "occupied_beds"]]
    model_path = os.path.join(tmp_path, "test_xgb.joblib")
    out_path = train_xgb_model(feature_df, target_column="occupied_beds", model_save_path=model_path)
    assert os.path.exists(out_path)

def test_train_prophet_model(tmp_path):
    # Load data from generated CSV
    csv_path = "./services/etl/occupancy_data.csv"
    df = pd.read_csv(csv_path)
    model_path = os.path.join(tmp_path, "test_prophet.joblib")
    out_path = train_prophet_model(df, model_save_path=model_path)
    assert os.path.exists(out_path)