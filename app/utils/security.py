# placeholder: простая проверка API key
from fastapi import Header, HTTPException
def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != "dev-key":
        raise HTTPException(status_code=401, detail="invalid api key")
