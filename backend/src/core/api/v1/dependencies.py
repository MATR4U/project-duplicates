# src/api/dependencies.py
from sqlalchemy.orm import sessionmaker
from src.database.DatabaseBase import DatabaseBase
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException
from fastapi import Depends
from sqlmodel import Session
from src.common.Service import MyService


def get_my_service(db: Session = Depends(DatabaseBase._get_session())) -> MyService:
    return MyService(db)

