from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.endpoints.Base import EndpointsBase
from src.api.v1.endpoints.EndpointItem import Item
from src.api.v1.schemas.SchemaItem import ItemCreate, ItemRead
from src.api.v1.dependencies import get_database_session  # Import your database session utility

router = APIRouter()
crud_item = EndpointsBase(Item)

@router.post("/items/", response_model=ItemRead)
def create_item(item: ItemCreate, db: Session = Depends(get_database_session)):
    return crud_item.create(db, obj_in=item)

@router.get("/items/{item_id}", response_model=ItemRead)
def read_item(item_id: int, db: Session = Depends(get_database_session)):
    db_item = crud_item.get(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# Additional endpoints for update and delete
