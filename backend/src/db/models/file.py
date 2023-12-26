from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class FileModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String)
    path = Column(String)
    size = Column(Integer)
    modification_time = Column(Float)
    access_time = Column(Float)
    creation_time = Column(Float)
    is_deleted = Column(Boolean)

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