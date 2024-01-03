from typing import Generic, TypeVar, Type, List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError
from sqlmodel import SQLModel
from fastapi import HTTPException

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

###
# When to Implement Specific CRUD Methods:
# You would only need to implement or override specific CRUD methods in the following scenarios:
# Custom Business Logic: If a particular model requires custom business logic during CRUD operations that are not covered by the generic methods.
# Additional Validations: If you need to perform additional validations or processing on the data before saving or updating it in the database.
# Complex Queries: If your read operations involve complex queries that are not just simple retrievals based on the primary key.
# Special Handling: If there are specific actions that need to be taken when deleting or updating records, such as cascading deletes or updating related records.
###

class EndpointsBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Initialize the CRUD object with a specific SQLModel model.
        """
        self.model = model

    @staticmethod
    def decode(data: Dict[str, Any], model: Type[BaseModel]) -> BaseModel:
        """
        Convert a dictionary to a Pydantic model.

        :param data: The dictionary to be converted.
        :param model: The Pydantic model class for conversion.
        :return: An instance of the Pydantic model.
        """
        try:
            return model(**data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Invalid data: {e}")

    @staticmethod
    def encode(obj: Union[BaseModel, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert a Pydantic model or a dictionary to a dictionary.
        If the input is a Pydantic model, it will be exported to a dictionary.
        If it's already a dictionary, it will be returned as is.

        :param obj: The Pydantic model or dictionary to be converted.
        :return: A dictionary representation of the input.
        """
        return obj.dict(exclude_unset=True) if isinstance(obj, BaseModel) else obj

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Retrieve a single record by its ID.
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"Item with ID {id} not found")
        return obj

    def get_all(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Retrieve multiple records with optional pagination.
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: Union[CreateSchemaType, dict]) -> ModelType:
        """
        Create a new record in the database.
        Decide whether to use the direct approach or the superclass method.
        """
        if isinstance(obj_in, dict):
            # If obj_in is a dictionary, decode it and use the superclass method
            obj_in = self.decode(obj_in, CreateSchemaType)
            return super().create(db, obj_in=obj_in)
        else:
            # If obj_in is already a Pydantic model, use the direct approach
            return self.create_direct(db, obj_in=obj_in)

    def create_direct(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record in the database.
        """
        obj_in_data = self.encode(obj_in)
        db_obj = self.model(**obj_in_data)
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record in the database.
        Decide whether to use the direct approach or the superclass method.
        """
        if isinstance(obj_in, dict):
            # If obj_in is a dictionary, decode it and use the superclass method
            obj_in = self.decode(obj_in, UpdateSchemaType)
            return super().update(db, db_obj=db_obj, obj_in=obj_in)
        else:
            # If obj_in is already a Pydantic model, use the direct approach
            return self.update_direct(db, db_obj=db_obj, obj_in=obj_in)

    def update_direct(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record in the database directly.
        """
        update_data = self.encode(obj_in)
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Delete a record from the database.
        """
        obj = db.query(self.model).get(id)
        if obj:
            try:
                db.delete(obj)
                db.commit()
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
            return obj
        else:
            raise HTTPException(status_code=404, detail=f"Item with ID {id} not found")
