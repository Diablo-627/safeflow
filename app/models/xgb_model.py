import joblib
import pandas as pd
import os

# Загружаем модель и метаданные
MODEL_PATH = "app/models/xgb_v1.joblib"
META_PATH = "app/models/xgb_v1.meta.json"

model = joblib.load(MODEL_PATH)
meta = pd.read_json(META_PATH, typ="series")

def predict(data: pd.DataFrame):
    """Возвращает предсказания вероятности для входных данных"""
    # Убедимся, что все нужные фичи есть
    missing = [f for f in meta["features"] if f not in data.columns]
    if missing:
        raise ValueError(f"Отсутствуют признаки: {missing}")

    preds = model.predict_proba(data[meta["features"]])[:, 1]
    return preds

# Пример использования:
if __name__ == "__main__":
    test = pd.DataFrame([
        {"sensor_1": 20, "sensor_2": 10, "sensor_3": 6},
        {"sensor_1": 8, "sensor_2": 3, "sensor_3": 2}
    ])
    print(predict(test))
