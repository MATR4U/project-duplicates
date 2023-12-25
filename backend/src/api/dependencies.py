# src/api/dependencies.py
from sqlalchemy.orm import Session
from src.app import App

def get_database_session() -> Session:
    db = App.get_instance.get_db()
    try:
        yield db
    finally:
        db.close()

