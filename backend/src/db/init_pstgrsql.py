"""Defines files schema including methods for initializing and managing the database."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
#from sqlalchemy_utils import create_database

# Define the database URL for the PostgreSQL database
#TODO externalize in config file!
DATABASE_URL = "postgresql://myuser:mypassword@matr-db-postgres/mydb"

# Define a base class for your models
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init():
    _create_database()
    _create_tables()

def _create_database():
    try:
        # Attempt to create the database
        with engine.connect() as connection:
            connection.execute("commit")  # Ensure any pending transactions are committed
            connection.execute(f"CREATE DATABASE {engine.url.database}")

    except ProgrammingError:
        # Database already exists, no need to create it
        pass

def _create_tables():
    Base.metadata.create_all(bind=engine)

def _drop_tables():
    Base.metadata.drop_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
