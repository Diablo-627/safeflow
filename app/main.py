from fastapi import FastAPI

app = FastAPI()

# Добавь этот endpoint
@app.get("/")
async def root():
    return {"message": "Hello World", "status": "API is working!"}

# Остальные твои endpoints...
@app.get("/items/")
async def read_items():
    return [{"item": "Item 1"}, {"item": "Item 2"}]