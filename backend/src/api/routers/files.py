# src/api/files.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.models.file import File
from src.db.database import Database

router = APIRouter()

def get_database() -> Database:
    return Database.get_instance()

def get_database_session() -> Session:
    return get_database().SESSION

@router.get("/")
async def read(db: Session = Depends(get_database_session)):
    # Use the db as needed
    db.query(File).all()
    return {"Hello": "World"}

@router.post("/files/", response_model=File)
def create(file: File, db: Session = Depends(get_database_session)):
    item = File(**file.__dict__)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item