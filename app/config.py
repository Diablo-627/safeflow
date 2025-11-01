from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DATABASE_URL: str = Field("sqlite:///./dev.db", env="DATABASE_URL")
    ML_MODEL_PATH: str = Field("./ml/model.xgb", env="ML_MODEL_PATH")
    ALERT_1C_URL: str = Field("http://localhost:9001/alert", env="ALERT_1C_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
