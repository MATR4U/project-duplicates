import os
import json
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Config:
    CONFIG_FILE = 'config.json'
    config = None  # Class attribute to store config data
    args = None

    def __init__(self, args: argparse.Namespace):
        self.args = args
    
    def load_config(self, config_file=None):
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
            return self.load_config(self.args.config).get('source')
        else: return ""
    
    def get_destination(self):
        if self.args:
            return self.args.destination
        elif os.environ:
            return os.environ.get('DESTINATION')
        elif self.args.config:
            return self.load_config(self.args.config).get('destination')
        else:
            return ""

    def get_database_url(cls):
        # Check command line arguments, then environment variable, then config file
        if cls.args and cls.args.db_url:
            return cls.args.db_url
        elif os.environ.get('DB_URL'):
            return os.environ.get('DB_URL')
        else:
            return cls._read_config(cls.CONFIG_FILE)
        

    def _read_config(self, config=None):
        config = self.load_config(config)

        db_config = config.get('Database', {})
        db_type = db_config.get('db_type')
        db_user = db_config.get('db_user')
        db_password = db_config.get('db_password')
        db_host = db_config.get('db_host')
        db_port = db_config.get('db_port')
        db_name = db_config.get('db_name')

        url = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return url
