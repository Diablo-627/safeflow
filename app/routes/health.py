from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/")
def health():
    return {"status": "ok", "env": settings.ENV}
