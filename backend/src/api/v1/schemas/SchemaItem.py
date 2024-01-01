from pydantic import BaseModel
from typing import Optional


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    Description: Optional[str] = None


class ItemRead(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True

