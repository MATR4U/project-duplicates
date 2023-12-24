from sqlalchemy import Engine, Connection, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import ProgrammingError
#from sqlalchemy_utils import create_database
from src.utils.config import Config

class Database:

    DB_URL = None
    BASE = None
    SESSION: Session = None
    ENGINE: Engine = None

    def __init__(self, db_url):
        self.DB_URL = db_url
        self.BASE = declarative_base()
        self.ENGINE = self._create_engine(db_url)
        self.SESSION = self._create_session(self.ENGINE)
        self._create_database(self.ENGINE)
        self._create_tables()

    def _create_engine(self, db_url: str) -> Engine:
        return create_engine(db_url)

    def _create_database(self, engine: Engine):
        try:
            # Attempt to create the database
            with engine.connect() as connection:
                connection.execute("commit")  # Ensure any pending transactions are committed
                connection.execute(f"CREATE DATABASE {engine.url.database}")

        except ProgrammingError:
            # Database already exists, no need to create it
            pass

    def _create_session(self) -> Session:
        return sessionmaker(autocommit=False, autoflush=False, bind=self.ENGINE)

    def _create_tables(self):
        self.BASE.metadata.create_all(bind=self.ENGINE)

    def _drop_tables(self):
        self.BASE.metadata.drop_all(bind=self.ENGINE)

    def get_db(self):
        db = self.SESSION
        try:
            yield db
        finally:
            db.close()
