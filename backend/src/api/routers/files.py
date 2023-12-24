# src/api/files.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.models.file import File

router = APIRouter()

@router.get("/")
async def read(db_url: str = Depends(config.get_db_url())):
    # Use the db_url as needed
    return {"Hello": "World"}

@router.post("/files/", response_model=File)
def create(file: File, db: Session = Depends(get_database_session), db_url: str = Depends(get_db_url)):
    item = File(**file.__dict__)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item