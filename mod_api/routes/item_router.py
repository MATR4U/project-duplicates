# app/routes/item_routes.py
from fastapi import APIRouter
from mod_db.models.item_model import Item

router = APIRouter()

@router.post("/items/")
async def create_item(item: Item):
    return {"name": item.name, "description": item.description}

@router.get("/")
async def read_root():
    return {"Hello": "World"}