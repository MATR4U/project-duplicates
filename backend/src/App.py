import logging
from src.core.processor import Processor
from argparse import Namespace
from src.database.Postgresql import Postgresql
from src.api.ApiServer import APIServer
from src.config.Config import Config
from src.config.ConfigModel import ArgsConfig, AppConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class App:
    """
    Singleton class that represents the application. It handles the initialization
    and management of various components like configuration, processor, API server, and database.
    """
    _initialized = False
    _instance = None  # Singleton instance
    _args_config: ArgsConfig = None
    _config: Config = None
    _processor = None
    _api_server = None
    _db = None

    def __new__(cls, args: dict):
        """
        Ensures only one instance of the App class is created. Initializes the instance with arguments.
        """
        if cls._instance is None:
            cls._instance = super(App, cls).__new__(cls)
        return cls._instance

    def __init__(self, args: Namespace):
        """
        Initialize the application. This includes setting up configuration, database, API, and processor.
        The initialization only occurs once due to the singleton pattern.
        """

        if getattr(self, '_initialized', False):
            return

        try:
            self._args_config = ArgsConfig(**vars(args))
            self._config = Config(self._args_config)  # Returns the configuration instance.
            self._processor = Processor()
            self._api_server = APIServer()
            #self._db = Postgresql(self._config) #ToDo
            self._initialized = True
            logging.info("Application initialized successfully.")

        except Exception as e:
            logging.error(f"Error during App initialization: {e}")
            raise

    def run_api_server(self):
        self._api_server.run(self._config.get_config_api()['api_host'],
                            self._config.get_config_api()['api_port'],
                            self._config.get_config_api()['api_log_level'])
