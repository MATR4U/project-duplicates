from database.DatabaseBase import DatabaseBase
from config.Config import Config
from typing import Optional


class Postgresql(DatabaseBase):
    def __new__(cls, config: Optional[Config] = None, *args, **kwargs):
        """
        Ensures that only one instance of the Postgresql class is created,
        following the singleton pattern of DatabaseBase.
        """
        return super(Postgresql, cls).__new__(cls, config, *args, **kwargs)

    def __init__(self, config: Config):
        """
        Initialize the PostgreSQL-specific features, ensuring that the base
        initialization is also called.
        """
        super().__init__(config)
        self._initialize_postgresql(config)

    def _initialize_postgresql(self, config: Config):
        """
        PostgreSQL-specific initialization, if necessary.
        """
        # Add any PostgreSQL-specific initialization here.
        pass