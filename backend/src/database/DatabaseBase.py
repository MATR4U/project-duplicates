from typing import Optional, Any, Sequence
import logging
from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError, SQLAlchemyError
from sqlmodel import SQLModel, create_engine, Session
from src.config.Config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseBase:
    """
    Singleton class that manages the database connection and operations for the application.
    Uses SQLAlchemy to interact with the database.
    """
    _instance: Optional['DatabaseBase'] = None  # Private class-level instance attribute
    _initialized = False
    _db_url: str = None
    _engine: Engine = None

    def __new__(cls, config: Optional[Config] = None, *args, **kwargs):
        """
        Ensures that only one instance of the Database class is created.
        If the instance already exists, return it without needing the config.
        """
        if cls._instance is None:
            if config is None or not isinstance(config, Config):
                raise ValueError("A valid config is required for the first instantiation")

            cls._instance = super(DatabaseBase, cls).__new__(cls)

        return cls._instance

    def __init__(self, config: Config = None):
        if self._initialized:
            return

        # Validate config
        if not isinstance(config, Config):
            logging.error("Invalid configuration object provided.")
            raise TypeError("Expected a Config instance.")

        # Initialize database
        try:
            # initialization
            self._db_url = config.get_database_url()
            self._engine: Engine = self._create_engine(self._db_url)

            # Create database and tables
            self._initialize_database(config)

            self._initialized = True
            logging.info("Database successfully initialized.")

        except OperationalError as oe:
            logging.error(f"Operational error during database initialization: {oe}")
            raise  # Consider how to handle this in your application context
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemy error during database initialization: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during database initialization: {e}")
            raise

    def _initialize_database(self, config: Config):
        """Handles the initialization of the database and tables."""
        with self._get_session() as session:
            self._create_database(session, config.get_config_app().Database.db_name)
            self._create_tables(self._engine)

    @staticmethod
    def _create_engine(db_url) -> Engine:
        """
        Creates a new SQLAlchemy engine with enhanced error handling
        and optional configuration settings.
        """
        logging.info("Creating engine...")

        # Optional: Engine configuration settings
        engine_options = {
            "echo": False,  # Set to True to log all SQL statements (useful for debugging)
            "pool_pre_ping": True,  # Check for broken connections before checkout
            "pool_recycle": 3600,  # Time to recycle connections
            "pool_timeout": 30,    # Timeout for getting connections from the pool
            # Additional options can be added here as needed
        }

        try:
            engine = create_engine(db_url, **engine_options)
            return engine
        except SQLAlchemyError as e:
            logging.error(f"Error creating SQLAlchemy engine: {e}")
            raise  # Re-raise the exception or handle it as needed

    def _get_session(self) -> Session:
        """Create and return a new session."""
        if not self._engine:
            raise Exception("Database engine is not initialized.")
        return Session(self._engine)

    def _create_database(self, session: Session, db_name):
        """
        Creates a new database using the provided engine.
        """
        logging.info("Creating database...")

        try:
            t = text(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            session.execute(t)
        except ProgrammingError:
            logging.warning(f"Database '{self._db_url}' already exists, no need to create it.")
        except OperationalError:
            logging.error(f"Failed to connect to the database '{self._db_url}'.")
        except IntegrityError:
            logging.error(f"Failed to create the database '{self._db_url}' due to a constraint violation.")
        except Exception as e:
            logging.error(f"An unexpected error occurred while creating the database '{self._db_url}': {e}")

    @staticmethod
    def _create_tables(engine):
        # Create tables for all imported models
        SQLModel.metadata.create_all(engine)

    def execute(self, query: str) -> Sequence[Any]:
        """
        Execute a SQL query and return the results.
        """
        with self._get_session() as session:
            result = session.execute(text(query))
            all_rows = result.all()

            for row in all_rows:
                logging.info(f"Database Row '{row}'.")

            return all_rows
