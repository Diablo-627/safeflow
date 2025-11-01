# app/utils/security.py
from fastapi import Header, HTTPException, Depends
from app.config import settings

def verify_api_key(x_api_key: str | None = Header(None)):
    # If API_KEY is not configured — allow for dev mode
    if not settings.API_KEY:
        return True
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True
