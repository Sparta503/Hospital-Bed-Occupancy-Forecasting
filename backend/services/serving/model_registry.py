import os
import json
import joblib
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelRegistry:
    """Registry for managing trained forecasting models"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.metadata_file = self.models_dir / "model_metadata.json"
        self._metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load model metadata from file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"models": {}}
    
    def _save_metadata(self):
        """Save model metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self._metadata, f, indent=2)
    
    def register_model(
        self,
        model_name: str,
        model: Any,
        model_type: str,
        features: List[str],
        target: str,
        metrics: Dict[str, float],
        training_data_size: int,
        model_version: Optional[str] = None
    ) -> str:
        """Register a new model in the registry"""
        if model_version is None:
            model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        model_id = f"{model_name}_{model_version}"
        model_path = self.models_dir / f"{model_id}.joblib"
        
        # Save the model
        joblib.dump(model, model_path)
        
        # Update metadata
        self._metadata["models"][model_id] = {
            "model_name": model_name,
            "model_type": model_type,
            "model_version": model_version,
            "model_path": str(model_path),
            "features": features,
            "target": target,
            "metrics": metrics,
            "training_data_size": training_data_size,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self._save_metadata()
        logger.info(f"Model {model_id} registered successfully")
        return model_id
    
    def load_model(self, model_id: str) -> Any:
        """Load a model from the registry"""
        if model_id not in self._metadata["models"]:
            raise ValueError(f"Model {model_id} not found in registry")
        
        model_path = self._metadata["models"][model_id]["model_path"]
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        return joblib.load(model_path)
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get model metadata"""
        if model_id not in self._metadata["models"]:
            raise ValueError(f"Model {model_id} not found in registry")
        
        return self._metadata["models"][model_id]
    
    def list_models(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all models or models with specific name"""
        models = []
        for model_id, info in self._metadata["models"].items():
            if model_name is None or info["model_name"] == model_name:
                models.append({"model_id": model_id, **info})
        
        # Sort by creation date (newest first)
        models.sort(key=lambda x: x["created_at"], reverse=True)
        return models
    
    def get_best_model(self, model_name: str, metric: str = "rmse") -> Optional[str]:
        """Get the best model based on a specific metric"""
        models = self.list_models(model_name)
        
        if not models:
            return None
        
        # Find model with best metric (lower is better for rmse, mae)
        best_model = min(models, key=lambda x: x["metrics"].get(metric, float('inf')))
        return best_model["model_id"]
    
    def deactivate_model(self, model_id: str):
        """Deactivate a model"""
        if model_id not in self._metadata["models"]:
            raise ValueError(f"Model {model_id} not found in registry")
        
        self._metadata["models"][model_id]["status"] = "inactive"
        self._save_metadata()
        logger.info(f"Model {model_id} deactivated")
    
    def delete_model(self, model_id: str):
        """Delete a model from the registry"""
        if model_id not in self._metadata["models"]:
            raise ValueError(f"Model {model_id} not found in registry")
        
        # Delete model file
        model_path = self._metadata["models"][model_id]["model_path"]
        if Path(model_path).exists():
            Path(model_path).unlink()
        
        # Remove from metadata
        del self._metadata["models"][model_id]
        self._save_metadata()
        logger.info(f"Model {model_id} deleted")
    
    def get_active_models(self) -> List[str]:
        """Get list of active model IDs"""
        return [
            model_id for model_id, info in self._metadata["models"].items()
            if info["status"] == "active"
        ]

# Global model registry instance
model_registry = ModelRegistry()