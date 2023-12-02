# app/models/item_model.py
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str = None