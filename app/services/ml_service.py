# app/services/ml_service.py
from typing import List, Dict, Optional
import os
import logging

logger = logging.getLogger("ml_service")

class MLService:
    _instance = None

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv("ML_MODEL_PATH", "./ml/model.xgb")
        self.model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MLService()
            try:
                cls._instance.warmup()
            except Exception as e:
                logger.warning("MLService warmup failed: %s — continuing with stub.", e)
        return cls._instance

    def warmup(self):
        # If a real model exists, load it here (joblib/xgboost/pickle)
        if os.path.exists(self.model_path):
            # placeholder: actual loading will be implemented by ML owner
            logger.info("Found model artifact at %s, but loader not implemented in app.", self.model_path)
            self.model = "loaded"
        else:
            logger.info("No model artifact found at %s — running in stub mode.", self.model_path)
            self.model = None

    def predict_batch(self, features: List[Dict]) -> List[float]:
        # stub inference: use normalized value feature 'value_norm' if present
        results = []
        for f in features:
            v = float(f.get("value_norm", 0.0))
            p = min(1.0, max(0.0, 0.05 + v * 0.9))
            results.append(p)
        return results
