from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models.all import Base

DATABASE_URL = "sqlite:///./test.db"  # Example SQLite database URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)