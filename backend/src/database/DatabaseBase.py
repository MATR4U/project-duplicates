from typing import Optional, List, Tuple, Any, Sequence
import logging
from sqlalchemy import Connection, Engine, text, Row
from sqlalchemy.engine import TupleResult
from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError
from sqlmodel import SQLModel, create_engine, Session
from src.common.Config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseBase:
    """
    Singleton class that manages the database connection and operations for the application.
    Uses SQLAlchemy to interact with the database.
    """
    _instance: Optional['DatabaseBase'] = None  # Private class-level instance attribute
    _initialized = False
    db_url: str = None
    engine: Engine = None

    def __new__(cls, config: Optional[Config] = None, *args, **kwargs):
        """
        Ensures that only one instance of the Database class is created.
        If the instance already exists, return it without needing the config.
        """
        if cls._instance is None:
            if config is None or not isinstance(config, Config):
                raise ValueError("A valid config is required for the first instantiation")

            cls._instance = super(DatabaseBase, cls).__new__(cls)
            cls._instance._initialize(config)

        return cls._instance

    def _initialize(self, config: Config):
        try:
            if not self._initialized:
                self.db_url = config.get_database_url()
                self.engine: Engine = self._create_engine(self.db_url)
                self._create_database(self._get_session(), config.get_config_db()['db_name'])
                self.create_tables(self.engine)
                self._initialized = True
                self._instance = self  # ToDo check why needed < __new__ exists >
        except OperationalError as oe:
            logging.error(f"Failed to connect to the database: {oe}")
        except Exception as e:
            logging.error(f"Failed to initialize the database: {e}")

    def _create_engine(self, db_url) -> Engine:
        """
        Creates a new SQLAlchemy engine.
        """
        logging.info("Creating engine...")
        engine = create_engine(db_url)
        SQLModel.metadata.create_all(engine)

        return engine

    def _get_session(self):
        return Session(self.engine)

    def _create_database(self, session: Session, db_name):
        """
        Creates a new database using the provided engine.
        """
        logging.info("Creating database...")

        try:
            t = text(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            session.execute(t)
        except ProgrammingError:
            logging.warning(f"Database '{self.db_url}' already exists, no need to create it.")
        except OperationalError:
            logging.error(f"Failed to connect to the database '{self.db_url}'.")
        except IntegrityError:
            logging.error(f"Failed to create the database '{self.db_url}' due to a constraint violation.")
        except Exception as e:
            logging.error(f"An unexpected error occurred while creating the database '{self.db_url}': {e}")

    def create_tables(self, engine):
        # TODO
        # Make sure all your SQLModel models are imported before this step
        # For example:
        from src.database.models.ecommerce import User, Product, Order, OrderItem
        from src.database.models.item import Item
        SQLModel.metadata.create_all(engine)

    def execute(self, query: str) -> Sequence[Row[tuple[Any, ...] | Any]]:
        """
        Execute a SQL query and return the results.
        """
        with self._get_session() as session:
            result = session.execute(text(query))
            all_rows = result.all()

            for row in all_rows:
                logging.info(f"Database Row '{row}'.")

            return all_rows
