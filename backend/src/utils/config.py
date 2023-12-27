import os
import json
import logging
import argparse
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

class Config:
    _lock = threading.Lock()
    _instance = None  # Class attribute to store the singleton instance
    _initialized = False

    CONFIG_FILE = 'config.json'
    config = None  # Class attribute to store config data
    args = None
    

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.config = self._load_config()
            self._initialized = True

    def _load_config(self, config_file=None):
        if self.config is None:
            config_file = config_file or self.CONFIG_FILE
            try:
                with open(config_file, 'r') as file:
                    self.config = json.load(file)
            except FileNotFoundError:
                self.config = {}
            except Exception as e:
                logging.error("Error loading configuration from {}: {}".format(config_file, e))
                self.config = {}
        return self.config
        
    def get_source(self):
        if self.args:
            return self.args.source
        elif os.environ:
            return os.environ.get('SOURCE')
        elif self.args.config:
            return self._load_config(self.args.config).get('source')
        else:
            return ""
    
    def get_destination(self):
        if self.args:
            return self.args.destination
        elif os.environ:
            return os.environ.get('DESTINATION')
        elif self.args.config:
            return self._load_config(self.args.config).get('destination')
        else:
            return ""

    def get_database_url(cls):
        # Check command line arguments, then environment variable, then config file
        if cls.args and cls.args.db_url:
            return cls.args.db_url
        elif os.environ.get('DB_URL'):
            return os.environ.get('DB_URL')
        else:
            return cls.get_config_db()
    
    @classmethod
    def get_config_api(cls):
        # Check command line arguments, then environment variable, then config file
        config = cls.config
        
        if cls.args and cls.args.api_host:
            api_host = cls.args.api_host
        else:
            api_host = config.get('API', {}).get('api_host', '0.0.0.0')

        if cls.args and cls.args.api_port:
            api_port = cls.args.api_port
        else:
            api_port = config.get('API', {}).get('api_port', '8000')

        if cls.args and cls.args.api_log_level:
            api_log_level = cls.args.api_log_level
        else:
            api_log_level = config.get('API', {}).get('api_log_level', 'info')

        return {
            'api_host': api_host,
            'api_port': int(api_port),
            'api_log_level': api_log_level
        }

    @classmethod
    def get_config_db(self):
        config = self._load_config(self)

        db_config = config.get('Database', {})
        db_type = db_config.get('db_type', 'postgresql')
        db_user = db_config.get('db_user', 'myuser')
        db_password = db_config.get('db_password', 'mypassword')
        db_host = db_config.get('db_host', 'localhost')
        db_port = db_config.get('db_port', '5432')
        db_name = db_config.get('db_name', 'mydb')
        db_url = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
       
        return db_url
