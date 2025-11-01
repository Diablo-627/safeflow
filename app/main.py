from fastapi import FastAPI
from app.routes import predict, health
from app.config import settings

app = FastAPI(title="safeflow-app", version="0.1.0")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(predict.router, prefix="/predict", tags=["predict"])

@app.on_event("startup")
def startup_event():
    # заранее прогрузим модель
    from app.services.ml_service import MLService
    MLService.get_instance().warmup()
  