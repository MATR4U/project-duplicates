# src/api/dependencies.py
from sqlalchemy.orm import sessionmaker
from src.database.DatabaseBase import DatabaseBase
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException
from fastapi import Depends
from sqlmodel import Session
from src.common.Service import MyService


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=DatabaseBase()._engine)


def get_my_service(db: Session = Depends(DatabaseBase._get_session())) -> MyService:
    return MyService(db)


def get_database_session():
    db = SessionLocal()
    try:
        yield db
    except OperationalError:
        raise HTTPException(status_code=500, detail="Could not connect to the database.")
    finally:
        db.close()
