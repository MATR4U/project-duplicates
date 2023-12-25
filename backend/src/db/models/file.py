# app/models/file.py
from pydantic import BaseModel

class FileBase(BaseModel):
    hash: str
    path: str
    size: int
    modification_time: float
    access_time: float
    creation_time: float
    is_deleted: bool

class FileCreate(FileBase):
    pass

class File(FileBase):
    id: int
    date_added: str