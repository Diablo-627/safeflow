# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DATABASE_URL: str = Field("sqlite:///./dev.db")
    ML_MODEL_PATH: str = Field("./ml/model.xgb")
    ALERT_1C_URL: str = Field("http://localhost:9001/alert")
    API_KEY: str | None = None

    # tell pydantic-settings to load from .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
