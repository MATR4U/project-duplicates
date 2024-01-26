from pydantic import BaseModel
from typing import Optional


class HealthCreate(BaseModel):
    name: str
    description: str


class HealthUpdate(BaseModel):
    name: Optional[str] = None
    Description: Optional[str] = None


class HealthRead(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True