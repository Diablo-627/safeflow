import json
import os
import time
import joblib
import pandas as pd

# Пути
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/model.pkl"))
live_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/live_sensor.ndjson"))

# Загружаем модель
model = joblib.load(model_path)
print(f"✅ Модель загружена из {model_path}")

# Используем те же признаки, на которых обучались
features = ["reading", "true_temp", "bias", "scale", "noise_std"]

print("📡 Ожидание данных в live_sensor.ndjson... (Ctrl+C для остановки)\n")

# Храним количество уже обработанных строк
processed = 0

while True:
    if not os.path.exists(live_path):
        time.sleep(1)
        continue

    with open(live_path, "r") as f:
        lines = f.readlines()

    # Если появились новые строки
    if len(lines) > processed:
        new_lines = lines[processed:]
        processed = len(lines)

        for line in new_lines:
            rec = json.loads(line)

            # Распаковка params
            params = rec.get("params", {})
            rec["bias"] = params.get("bias", 0.0)
            rec["scale"] = params.get("scale", 1.0)
            rec["noise_std"] = params.get("noise_std", 0.0)

            # Преобразуем в DataFrame для предсказания
            df = pd.DataFrame([rec])
            X = df[features]

            pred = model.predict(X)[0]
            probas = model.predict_proba(X)[0]
            prob_str = ", ".join(f"{cls}:{p:.2f}" for cls, p in zip(model.classes_, probas))

            print(f"[{rec['timestamp']}] 🔍 {pred.upper()} ({prob_str}) | reading={rec['reading']:.2f}")

    time.sleep(1)
