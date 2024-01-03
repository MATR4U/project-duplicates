import logging
from src.core.processor import Processor
from src.api.ApiServer import APIServer
from src.common.Config import Config
from src.database.Postgresql import Postgresql

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class App:
    _instance = None  # Private class-level instance attribute
    _initialized = False

    _args = None
    _config = None
    _processor = None
    _api = None
    _db = None

    def __new__(cls, args=None, **kwargs):
        if cls._instance is None:
            cls._instance = super(App, cls).__new__(cls)
            cls._instance._args = args
        return cls._instance

    def __init__(self, args=None):
        # Prevent re-initialization
        if self._initialized:
            return

        # Singleton initialization logic here
        self._args = args
        self._config = Config(args)
        self._initialized = True

    def processor(self):
        if self._processor is None:
            self._processor = Processor()
        return self._processor

    def api(self):
        if self._api is None:
            self._api = APIServer()
        return self._api

    def config(self):
        if self._config is None:
            self._config = Config(self._args)
        return self._config

    def db(self):
        if self._db is None:
            self._db = Postgresql(self.config())
        return self._db

    def run_db(self):
        # Example usage of db
        # TODO: Refactor health check
        # result = self.db.execute("SELECT * FROM health_check")
        pass

    def run_api(self):
        self.api().run(self._config.get_config())

    def run_cli(self):
        # TODO: Implement CLI logic
        pass