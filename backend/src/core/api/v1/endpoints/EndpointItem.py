from core.api.v1.endpoints.Base import EndpointsBase  # Import your CRUDBase class
from src.database.models.item import Item  # Import your SQLModel Item class
from core.api.v1.schemas.Item import ItemCreate, ItemUpdate  # Import your Pydantic schemas
from typing import Type


class EndpointItem(EndpointsBase[Item, ItemCreate, ItemUpdate]):
    def __init__(self, model: Type[Item]):
        super().__init__(model)

    # If you need to customize any CRUD methods specifically for Item, you can do it here.
