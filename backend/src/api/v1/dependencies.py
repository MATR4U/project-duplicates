# src/api/dependencies.py
from sqlalchemy.orm import Session
from src.database.DatabaseBase import DatabaseBase
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException

def get_database_session() -> Session:
    db = DatabaseBase()
    try:
        yield db
    except OperationalError:
        # Handle database connection errors here
        raise HTTPException(status_code=500, detail="Could not connect to the database.")
    finally:
        db.close()
