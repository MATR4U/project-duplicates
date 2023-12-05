# app/models/item_model.py
from pydantic import BaseModel

class File(BaseModel):
    path: str
    hash: str = None

    