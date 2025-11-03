import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# === Пути ===
data_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/train_sensor.ndjson")
)
model_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/model.pkl")
)

# === Загрузка данных ===
records = []
with open(data_path, "r") as f:
    for line in f:
        rec = json.loads(line)
        # распакуем params вручную
        params = rec.get("params", {})
        rec["bias"] = params.get("bias", 0.0)
        rec["scale"] = params.get("scale", 1.0)
        rec["noise_std"] = params.get("noise_std", 0.0)
        records.append(rec)

df = pd.DataFrame(records)
print("✅ Загружено записей:", len(df))
print("Поля:", list(df.columns))

# === Признаки и целевая переменная ===
features = ["reading", "true_temp", "bias", "scale", "noise_std"]
target = "health_state"

X = df[features].fillna(0)
y = df[target]

# === Разделение данных ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# === Обучение модели ===
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# === Оценка ===
y_pred = model.predict(X_test)
print("\n=== Отчёт по точности ===")
print(classification_report(y_test, y_pred))

# === Сохранение модели ===
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(model, model_path)
print(f"\n✅ Модель сохранена: {model_path}")
