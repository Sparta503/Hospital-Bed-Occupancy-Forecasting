import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
import logging
from .model_registry import model_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BasePredictor(ABC):
    """Abstract base class for predictors"""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.model = None
        self.model_info = None
        self._load_model()
    
    def _load_model(self):
        """Load model from registry"""
        try:
            self.model = model_registry.load_model(self.model_id)
            self.model_info = model_registry.get_model_info(self.model_id)
            logger.info(f"Model {self.model_id} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_id}: {str(e)}")
            raise
    
    @abstractmethod
    def preprocess_input(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess input data for prediction"""
        pass
    
    @abstractmethod
    def postprocess_output(self, prediction: Any) -> Dict[str, Any]:
        """Postprocess model output"""
        pass
    
    @abstractmethod
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction"""
        pass

class BedOccupancyPredictor(BasePredictor):
    """Predictor for hospital bed occupancy forecasting"""
    
    def __init__(self, model_id: str):
        super().__init__(model_id)
        self.features = self.model_info.get("features", [])
        self.target = self.model_info.get("target", "occupied_beds")
    
    def preprocess_input(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess input data for bed occupancy prediction"""
        # Convert input to DataFrame
        df = pd.DataFrame([input_data])
        
        # Feature engineering
        df = self._create_time_features(df)
        df = self._create_lag_features(df)
        df = self._create_rolling_features(df)
        
        # Ensure all required features are present
        for feature in self.features:
            if feature not in df.columns:
                df[feature] = 0  # Default value for missing features
        
        # Select only required features in the correct order
        df = df[self.features]
        
        return df
    
    def _create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        if 'record_date' in df.columns:
            df['record_date'] = pd.to_datetime(df['record_date'])
            df['year'] = df['record_date'].dt.year
            df['month'] =