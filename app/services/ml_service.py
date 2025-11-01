import os
from typing import List
from app.config import settings

class MLService:
    _instance = None

    def __init__(self, model_path=None):
        self.model_path = model_path or settings.ML_MODEL_PATH
        # В проде загрузим XGBoost/ONNX/torch модель
        # Здесь — простая заглушка
        self._model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MLService()
        return cls._instance

    def warmup(self):
        # simulate model load
        if not os.path.exists(self.model_path):
            # создадим пустой файл как маркер
            open(self.model_path, "a").close()
        self._model = "dummy_model_loaded"

    def predict_batch(self, features: List[dict]) -> List[float]:
        # features: list of dicts -> возвращаем p_fail в [0,1]
        out = []
        for f in features:
            # очень простая логика: чем выше "value_norm", тем выше p
            v = f.get("value_norm", 0.0)
            p = min(1.0, max(0.0, 0.1 + v * 0.8))
            out.append(p)
        return out
