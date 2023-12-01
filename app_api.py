# FastAPI backend
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None

@app.post("/items/")
async def create_item(item: Item):
    return {"name": item.name, "description": item.description}

@app.get("/")
async def read_root():
    return {"Hello": "World"}