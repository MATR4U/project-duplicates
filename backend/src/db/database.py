from typing import Optional
import logging
from sqlalchemy import Engine, Connection, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.exc import ProgrammingError, OperationalError, SQLAlchemyError, IntegrityError


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    """
    Singleton class that manages the database connection and operations for the application.
    Uses SQLAlchemy to interact with the database.
    """

    _instance: Optional['Database'] = None  # Private class-level instance attribute
    _initialized = False
    DB_URL: str = None
    BASE = None
    SESSION: Session = None
    ENGINE: Engine = None

    def __new__(cls, db_url=None, *args, **kwargs):
        """
        Ensures that only one instance of the Database class is created.
        """
        if not cls._instance:
            if db_url is None:
                raise ValueError("A db_url is required for the first instantiation")
        
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize(db_url)
        elif db_url is not None:
            raise ValueError("db_url should only be provided on the first instantiation")
        
        return cls._instance

    def _create_engine(self, db_url) -> Engine:
        """
        Creates a new SQLAlchemy engine.
        """
        logging.info("Creating engine...")
        return create_engine(db_url)

    def _create_database(self, engine):
        """
        Creates a new database using the provided engine.
        """
        logging.info("Creating database...")

        try:
            connection: Connection = self._connect_database(engine)
            if connection:
                connection.execute(f"CREATE DATABASE {self.ENGINE.url.database}")
        except ProgrammingError:
            logging.warning(f"Database '{self.ENGINE.url.database}' already exists, no need to create it.")
        except OperationalError:
            logging.error(f"Failed to connect to the database '{self.ENGINE.url.database}'.")
        except IntegrityError:
            logging.error(f"Failed to create the database '{self.ENGINE.url.database}' due to a constraint violation.")
        except Exception as e:
            logging.error(f"An unexpected error occurred while creating the database '{self.ENGINE.url.database}': {e}")

    def _connect_database(self, engine):
        try:
            return engine.connect()
        except OperationalError as oe:
            logging.error(f"Failed to connect to the database: {oe}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def _create_session(self, engine) -> Session:
        try:
            if engine is None:
                raise ValueError("Database Engine is not initialized.")
            session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return session
        except Exception as e:
            logging.error(f"Failed to create session: {e}")
            return None

    def _create_tables(self, base, engine):
        try:
            if base is None or engine is None:
                raise ValueError("BASE or ENGINE is not initialized.")
            
            from src.models.ecommerce import Order, Product, User, OrderItem
            self.BASE.metadata.create_all(bind=engine)
        except Exception as e:
            logging.error(f"Failed to create tables: {e}")

    def _drop_tables(self, base, engine):
        try:
            if base is None or engine is None:
                raise ValueError("BASE or ENGINE is not initialized.")
            base.metadata.drop_all(bind=engine)
        except Exception as e:
            logging.error(f"Failed to drop tables: {e}")

    def _initialize(self, db_url):
        try:
            if not self._initialized:
                self.DB_URL = db_url
                self.BASE = declarative_base()
                self.ENGINE = self._create_engine(self.DB_URL)
                self.SESSION = self._create_session(self.ENGINE)
                self._create_database(self.ENGINE)
                self._create_tables(self.BASE, self.ENGINE)
                #TODO chekc
                #
                self._initialized = True
                self._instance = self
        except OperationalError as oe:
            logging.error(f"Failed to connect to the database: {oe}")
        except Exception as e:
            logging.error(f"Failed to initialize the database: {e}")

    @classmethod
    def get_instance(cls) -> 'Database':
        try:
            if not cls._instance:
                cls._instance = cls()
            return cls._instance
        except SQLAlchemyError as e:
            logging.error(f"Failed to get instance due to SQLAlchemy error: {e}")
            return None
        except Exception as e:
            logging.error(f"Failed to get instance due to unexpected error: {e}")
            return None
        
    def execute(self, query):
        """
        Execute a SQL query and return the results.
        """
        try:
            # Create a new Session
            session = self.SESSION()

            # Convert the query to a text object
            query = text(query)

            # Execute the query
            result = session.execute(query)

            # Fetch the results
            rows = result.fetchall()

            return rows

        except Exception as e:
            logging.error(f"Failed to execute query '{query}' due to unexpected error: {e}")
            return None
        finally:
            # Close the session
            session.close()