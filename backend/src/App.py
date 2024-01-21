import logging
from src.core.processor import Processor
from src.api.ApiServer import APIServer
from src.common.Config import Config
from src.database.Postgresql import Postgresql

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class App:
    """
    Singleton class that represents the application. It handles the initialization
    and management of various components like configuration, processor, API server, and database.
    """
    _initialized = False
    _instance = None  # Singleton instance
    _args = None
    _config = None
    _processor = None
    _api = None
    _db = None

    def __new__(cls, args=None, **kwargs):
        """
        Ensures only one instance of the App class is created. Initializes the instance with arguments.
        """
        if cls._instance is None:
            cls._instance = super(App, cls).__new__(cls)
            cls._instance._args = args
        return cls._instance

    def __init__(self, args=None):
        """
        Initialize the application. This includes setting up configuration, database, API, and processor.
        The initialization only occurs once due to the singleton pattern.
        """
        if getattr(self, '_initialized', False):
            return

        try:
            self._args = args
            self._config = Config(self._args)  #Returns the configuration instance, creating it if it doesn't exist.
            self._processor = Processor()
            self._api = APIServer().run(self._config.get_json())
            self._db = Postgresql(self._config)
            self._initialized = True
            logging.info("Application initialized successfully.")

        except Exception as e:
            logging.error(f"Error during App initialization: {e}")
            raise

    def run_api(self):
        self._api.run(self._config.get_json())