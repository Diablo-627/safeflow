import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import joblib
import os

# Загружаем данные
df = pd.read_csv("ml/data/train_dataset.csv")

# Проверяем баланс классов
print("✅ Распределение целевой переменной:")
print(df['target'].value_counts())

# Разделяем фичи и целевую переменную
X = df.drop("target", axis=1)
y = df["target"]

# Разделяем train/test с сохранением соотношения классов
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Обучаем модель
model = XGBClassifier(
    n_estimators=50,
    max_depth=3,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)
model.fit(X_train, y_train)

# Предсказания и метрика
preds = model.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, preds)
print(f"🎯 ROC AUC: {roc_auc:.3f}")

# Сохраняем модель и метаданные
os.makedirs("app/models", exist_ok=True)
joblib.dump(model, "app/models/xgb_v1.joblib")

meta = {
    "roc_auc": float(roc_auc),
    "features": list(X.columns),
    "version": "xgb_v1"
}
pd.Series(meta).to_json("app/models/xgb_v1.meta.json")

print("✅ Модель и метаданные сохранены в app/models/")
