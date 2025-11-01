

---

```markdown
# 🧠 SafeFlow — Backend (Danil)

## 👨‍💻 Автор: Данил
**Роль в проекте:**  
Разработчик ядра приложения (`app/`): отвечает за реализацию онлайн-инференса, API, бизнес-логику, ETL в реальном времени, взаимодействие с базой данных и 1С.  
Фокус — **инженерия данных и архитектура FastAPI-сервиса**.

---

## 📂 Зона ответственности
Данил отвечает за все компоненты внутри директории `app/`, а также их интеграцию с остальными модулями.

### Основные папки:
```

app/
├─ main.py                # Точка входа FastAPI
├─ config.py              # Конфигурации (env, secrets, paths)
├─ routes/                # HTTP endpoints (predict, health, etc.)
├─ services/              # Логика инференса, ETL и нотификаций
├─ db/                    # Работа с TimescaleDB / Postgres
├─ models/                # Обёртки над ML-моделями (предоставленные Батырханом)
├─ utils/                 # Утилиты, security, общие функции
└─ requirements.txt       # Runtime-зависимости

````

---

## 🧩 Основные обязанности

| Категория | Обязанность | Цель |
|------------|--------------|------|
| **API** | Разработка REST-интерфейсов `/predict`, `/health` | Получение данных и возврат прогноза |
| **ML-инференс** | Подключение обученной модели (из `app/models`) | Реализация онлайн-прогнозирования |
| **ETL online** | Реализация feature extraction в реальном времени | Преобразование входных данных в фичи |
| **База данных** | Взаимодействие с TimescaleDB (`app/db/timeseries.py`) | Сбор и хранение телеметрии |
| **Интеграция с 1С** | Вызов `alert_dispatcher` при превышении порогов | Отправка уведомлений о поломках |
| **Безопасность** | Авторизация, API key, basic logging | Контроль доступа к сервису |
| **Docker/Deploy** | Подготовка `Dockerfile.app`, интеграция в compose | Упрощение локального и серверного запуска |
| **Тестирование** | Unit + интеграционные тесты (`tests/`) | Проверка корректности логики и API |

---

## 🚀 Текущие задачи (активный спринт)

### 🧱 Этап 1 — Базовая структура приложения
- [x] Создать каркас FastAPI (`app/main.py`, `routes/`).
- [x] Добавить `/health` endpoint.
- [ ] Настроить `app/config.py` (MODEL_PATH, DB_URL, 1C_URL, API_KEY).
- [ ] Добавить базовый Dockerfile (`docker/Dockerfile.app`).

### ⚙️ Этап 2 — Инференс и ETL
- [ ] Реализовать `app/services/ml_service.py`:
  - загрузка модели (из `app/models/xgb_v*.json`);
  - метод `predict_from_raw(payload)` → score.
- [ ] Написать `app/services/etl.py`:
  - feature engineering (rolling averages, delta, last value);
  - валидация входных данных.
- [ ] Создать `app/utils/features.py` — общие функции для обработки телеметрии.

### 📡 Этап 3 — API `/predict`
- [ ] `app/routes/predict.py`:
  - Pydantic-схемы входа/выхода;
  - валидация данных;
  - вызов `ml_service` + `etl` + `alert_dispatcher`.
- [ ] Пример запроса:
  ```bash
  curl -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"device_id":"m1","sensors":{"temp":23.4,"vibration":0.02}}'
````

### 🧾 Этап 4 — TimescaleDB / БД

* [ ] Реализовать `app/db/timeseries.py`:

  * функции `write_telemetry()` и `read_window()`.
  * тесты с SQLite в dev-режиме.
* [ ] Добавить health-check подключения к БД.

### 🔔 Этап 5 — Интеграция с 1С

* [ ] Интегрировать `alert_dispatcher` (на основе версии Батырхана).
* [ ] При превышении порога отправлять POST в `1C_URL`.

### 🧪 Этап 6 — Тестирование

* [ ] `tests/test_predict.py` — проверить `/predict` и формат ответа.
* [ ] `tests/test_etl_online.py` — тестировать feature-пайплайн.
* [ ] `tests/test_db.py` — CRUD для телеметрии.

---

## 🧰 Технический стек

* **Backend:** FastAPI, Pydantic, Uvicorn
* **ML-инференс:** XGBoost / Joblib модель (предоставляется Батырханом)
* **База данных:** TimescaleDB / PostgreSQL (SQLAlchemy)
* **Инфраструктура:** Docker, docker-compose
* **Тесты:** Pytest
* **Интеграция:** HTTP (1C stub endpoint)

---

## 🧠 Локальный запуск

```bash
# Установить зависимости
pip install -r app/requirements.txt

# Запустить сервис
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Проверить доступность
curl http://localhost:8000/health
```

---

## 🐳 Docker

```bash
docker build -t safeflow-app -f docker/Dockerfile.app .
docker run -p 8000:8000 safeflow-app
```

Или через `docker-compose` (при совместном запуске с симулятором и БД):

```bash
docker-compose up --build
```

---

## 🧩 Совместная работа с Батырханом

| Модуль                                        | Ответственный    | Контакт                        |
| --------------------------------------------- | ---------------- | ------------------------------ |
| **ML Training (`ml/`)**                       | Батырхан         | предоставляет обученные модели |
| **Model Wrapper (`app/models/xgb_model.py`)** | Батырхан         | формирует формат модели        |
| **Alert Dispatcher**                          | Батырхан         | реализует отправку алертов     |
| **Integration Test**                          | Данил + Батырхан | проверка end-to-end цикла      |

---

## ✅ Цель текущего этапа

**К концу спринта №1:**

* Рабочий FastAPI `/predict`, подключённая модель, alert в 1С stub.
* Симулятор может отправить данные → модель → предсказание → 1С лог.
* Минимум 70% покрытие тестами ключевых функций.

---

© SafeFlow ML Predictive Analytics — 2025
Автор раздела: **Данил**
Версия: `v0.1-dev`

```
