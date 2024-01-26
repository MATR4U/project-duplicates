# src/api/files.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.models.item import Item

router = APIRouter()


def get_database_session() -> Session:
    return Item().SESSION


@router.get("/")
async def read(db: Session = Depends(get_database_session)):
    # Use the db as needed
    db.query(Item).all()
    return {"Hello": "World"}


@router.post("/items/", response_model=Item)
def create(item: Item, db: Session = Depends(get_database_session)):
    item = Item(**item.__dict__)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
