# app/routes/item_routes.py
from fastapi import APIRouter
from src.db.models.file_model import File

router = APIRouter()

@router.post("/files/")
async def create(file: File):
    return {"path": file.path, "description": file.hash}

@router.get("/")
async def read():
    return {"Hello": "World"}

@app.post("/items/")
def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item