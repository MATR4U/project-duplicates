import os
import logging
import threading
from core.Config.ConfigFileHandler import ConfigFileHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


# ToDo Implement ConfigFileHandler
class Config:

    # TODO refactor into static config
    OSENV_DBURL = 'MATR_DB_URL'
    OSENV_SOURCE = 'MATR_SOURCE'
    OSENV_DESTINATION = 'MATR_DESTINATION'

    _lock = threading.Lock()
    _instance = None  # Class attribute to store the singleton instance
    _args = None
    _config_file = None
    _initialized = False

    def __new__(cls, args=None):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._args = args
        return cls._instance

    def __init__(self, args=None):
        if not self._initialized:
            self._config_file = ConfigFileHandler(self._args)  # Set the command-line arguments
            self._initialized = True

    def get_source(self):
        if self._args:
            return self._args.source
        elif os.environ:
            return os.environ.get(self.OSENV_SOURCE)
        elif self._args.get_json:
            return self._config_file.get_json().get_json('source')
        else:
            return ""
    
    def get_destination(self):
        if self._args:
            return self._args.destination
        elif os.environ:
            return os.environ.get(self.OSENV_DESTINATION)
        elif self._args.get_json:
            return self._config_file.get_json().get_json('destination')
        else:
            return ""

    def get_database_url(self):
        """
        Get the database URL from command line arguments, environment variable,
        or configuration file, in that order of precedence.
        """
        try:
            # Check command line arguments
            if self._args and self._args.db_url:
                logging.info("Getting database URL from command line arguments.")
                return self._args.db_url

            # Check environment variable
            db_url_env = os.environ.get(self.OSENV_DBURL)
            if db_url_env:
                logging.info("Getting database URL from environment variable.")
                return db_url_env

            # Fallback to configuration file
            cfg = self.get_config_db()
            if cfg and all(key in cfg for key in ['db_type', 'db_user', 'db_password', 'db_host', 'db_port', 'db_name']):
                logging.info("Getting database URL from configuration file.")
                db_url = f"{cfg['db_type']}://{cfg['db_user']}:{cfg['db_password']}@{cfg['db_host']}:{cfg['db_port']}/{cfg['db_name']}"
                return db_url
            else:
                raise ValueError("Database configuration is incomplete or missing.")

        except Exception as e:
            # Log and re-raise the exception for higher-level handling
            logging.error(f"Error in getting database URL: {e}")
            raise

    def get_json(self):
        """
        Retrieve database configuration from the loaded configuration file.
        Returns default values if specific configuration settings are not found.
        """
        try:
            config = self._config_file.get_json()
            return config

        except Exception as e:
            logging.error(f"Error retrieving configuration: {e}")
            # Optionally, re-raise the exception or return a default configuration
            raise  # or return {}

    def get_config_api(self):
        """
        Get the API configuration from command line arguments or configuration file.
        """
        # Retrieve the whole configuration dictionary safely
        config = self._config_file.get_json() if self._config_file else {}
        api_config = config.get('API', {})

        # API Host
        api_host = getattr(self._args, 'api_host', None)
        if api_host:
            logging.info("API host set from command line arguments.")
        else:
            api_host = api_config.get('api_host', '0.0.0.0')
            logging.info("API host set from configuration file.")

        # API Port
        api_port = getattr(self._args, 'api_port', None)
        if api_port:
            logging.info("API port set from command line arguments.")
        else:
            api_port = api_config.get('api_port', '8000')
            logging.info("API port set from configuration file.")

        # API Log Level
        api_log_level = getattr(self._args, 'api_log_level', None)
        if api_log_level:
            logging.info("API log level set from command line arguments.")
        else:
            api_log_level = api_config.get('api_log_level', 'info')
            logging.info("API log level set from configuration file.")

        return {
            'api_host': api_host,
            'api_port': int(api_port),
            'api_log_level': api_log_level
        }

    def get_config_db(self):
        """
        Retrieve database configuration from the loaded configuration file.
        Returns default values if specific configuration settings are not found.
        """
        try:
            db_config = self._config_file.get_json().get_json('Database', {})

            # Dictionary to store the final configuration
            final_config = {
                'db_type': db_config.get_json('db_type', 'postgresql'),
                'db_user': db_config.get_json('db_user', 'myuser'),
                'db_password': db_config.get_json('db_password', 'mypassword'),
                'db_host': db_config.get_json('db_host', 'localhost'),
                'db_port': db_config.get_json('db_port', '5432'),
                'db_name': db_config.get_json('db_name', 'mydb')
            }

            # Log warnings for any default values used
            for key, value in final_config.items():
                if key in db_config and db_config[key] is None:
                    logging.warning(f"Database configuration for '{key}' is missing; using default: '{value}'")
                elif key not in db_config:
                    logging.warning(f"Database configuration for '{key}' not found; using default: '{value}'")

            return final_config

        except Exception as e:
            logging.error(f"Error retrieving database configuration: {e}")
            # Optionally, re-raise the exception or return a default configuration
            raise  # or return {}
