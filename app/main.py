# app/main.py
from fastapi import FastAPI
from app.config import settings
from app.routes import health, predict

app = FastAPI(title="SafeFlow", version="0.1.0")

# include routers
app.include_router(health.router)
app.include_router(predict.router)

@app.get("/", tags=["root"])
def root():
    return {"message": "Hello World", "status": "API is working!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)