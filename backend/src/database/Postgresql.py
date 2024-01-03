from database.DatabaseBase import DatabaseBase
from sqlmodel import SQLModel, create_engine, Session
from src.common.Config import Config


class Postgresql(DatabaseBase):
    def _initialize(self, config: Config):
        # PostgreSQL-specific initialization, if necessary
        super()._initialize(config)  # Ensure base initialization is also called

