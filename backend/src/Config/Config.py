import os, logging, threading
from config.ConfigFileHandler import ConfigFileHandler
from config.ConfigModel import DatabaseConfig, ArgsConfig, APIConfig, AppConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


# ToDo Implement ConfigFileHandler
class Config:

    # TODO refactor into static config
    OSENV_DBURL = 'MATR_DB_URL'
    OSENV_SOURCE = 'MATR_SOURCE'
    OSENV_DESTINATION = 'MATR_DESTINATION'
    CONFIG_FILE_PATH = 'config.json'

    _lock = threading.Lock()
    _instance = None  # Class attribute to store the singleton instance
    _config_file_handler: ConfigFileHandler = None
    _config_file = None
    _args_config: ArgsConfig = None
    _config_file_path = CONFIG_FILE_PATH
    _initialized = False

    def __new__(cls, *args_config: ArgsConfig):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._args_config = args_config
        return cls._instance

    def __init__(self, args_config: ArgsConfig):
        if not self._initialized:
            self._args_config = args_config
            self._config_file_handler = ConfigFileHandler()  # Set the command-line arguments
            self._initialized = True

    def get_source(self):
        if self._args_config:
            return self._args_config.source
        elif os.environ:
            return os.environ.get(self.OSENV_SOURCE)
        elif self.get_config_app():
            return self.get_config_app().source
        else:
            raise
    
    def get_destination(self):
        if self._args_config:
            return self._args_config.destination
        elif os.environ:
            return os.environ.get(self.OSENV_DESTINATION)
        elif self.get_config_app():
            return self.get_config_app().destination
        else:
            raise

    def get_database_url(self):
        """
        Get the database URL from command line arguments, environment variable,
        or configuration file, in that order of precedence.
        """
        try:
            # Check command line arguments
            if self._args_config and self._args_config.db_url:
                logging.info("Getting database URL from command line arguments.")
                return self._args_config.db_url

            # Check environment variable
            db_url_env = os.environ.get(self.OSENV_DBURL)
            if db_url_env:
                logging.info("Getting database URL from environment variable.")
                return db_url_env

            # Fallback to configuration file
            logging.info("Getting database URL from configuration file.")
            cfg: DatabaseConfig = self.get_config_app().Database
            db_url = f"{cfg.db_type}://{cfg.db_user}:{cfg.db_password}@{cfg.db_host}:{cfg.db_port}/{cfg.db_name}"
            return db_url

        except Exception as e:
            # Log and re-raise the exception for higher-level handling
            logging.error(f"Error in getting database URL: {e}")
            raise

    def get_config_api(self):
        """
        Get the API configuration from command line arguments or configuration file.
        """
        # Retrieve the whole configuration dictionary safely
        try:
            app_config = self.get_config_app()

            if app_config and hasattr(app_config, 'API') and isinstance(app_config.API, APIConfig):
                api_config = app_config.API
            else:
                raise Exception("Error retrieving API configuration from AppConfig")

        except Exception as e:
            # Handle the specific error
            print(f"AppConfigError: {e}")
            raise

        return {
            'api_host': api_config.api_host,
            'api_port': int(api_config.api_port),
            'api_log_level': api_config.api_log_level
        }

    def get_config_app(self) -> AppConfig:
        """
        Get the current configuration.
        """
        with self._lock:
            return AppConfig(**self._config_file_handler.get_json())
