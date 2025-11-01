# app/routes/health.py
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    return {"status": "ok", "env": settings.ENV}
