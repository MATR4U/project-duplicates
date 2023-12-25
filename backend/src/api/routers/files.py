# src/api/files.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.init_pstgrsql import get_db
from src.db.models.file import File

router = APIRouter()

@router.get("/")
async def read():
    return {"Hello": "World"}

@router.post("/files/", response_model=File)
def create(file: File, db: Session = Depends(get_db)):
    item = File(**file.__dict__)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item