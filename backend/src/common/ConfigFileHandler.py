import os
import json
import logging
import hashlib
from threading import Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.Config.ConfigurationModel import AppConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ConfigFileHandler(FileSystemEventHandler):
    """
    Singleton class that handles reading a configuration file and monitoring
    it for changes.
    """
    _initialized = False
    _args = None
    _lock = Lock()  # Lock for thread-safety
    _path = 'config.json'  # Default path to the configuration file
    _instance = None  # Singleton instance
    _config_json = None    # Class attribute to store config data
    _observer = None  # Watchdog observer for file changes

    def __new__(cls, args=None):
        """
        Ensure only one instance of ConfigFileHandler is created.
        """
        if cls._instance is None:
            cls._instance = super(ConfigFileHandler, cls).__new__(cls)
            cls._instance._args = args
        return cls._instance

    def __init__(self, args=None):
        """
        Initialize the ConfigFileHandler instance. Load the configuration file
        and start the file observer to monitor for changes.
        """

        if getattr(self, '_initialized', False):
            return

        self._path = args.config or self._path
        if self._config_json is None:  # Initialize only once
            self._config_json = self._get_json()
            self._observer = Observer()  # Initialize the observer here
            self._start_watching_config()
        self.config_file_hash = self._calculate_file_hash()
        self._initialized = True

    def _get_json(self):
        """
        Load configuration from the specified file path. Defaults to the class
        CONFIG_FILE_PATH if no path is provided.
        """
        with self._lock:
            if not os.path.exists(self._path):
                logging.error(f"Configuration file not found at {self._path}")
                return {}

            try:
                with open(self._path, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from configuration file {self._path}: {e}")
            except IOError as e:
                logging.error(f"IOError while loading configuration from {self._path}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error loading configuration from {self._path}: {e}")

            return {}

    def _calculate_file_hash(self):
        """
        Calculate the MD5 hash of a file's contents.
        """
        hash_md5 = hashlib.md5()
        try:
            with open(self._path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except IOError as e:
            logging.error(f"Error reading file for hashing: {e}")
            return None

    def _reload_config(self):
        """
        Reload the configuration file.
        """
        with self._lock:
            self._config_json = self._get_json()

    def _start_watching_config(self):
        """
        Start the Watchdog observer to monitor configuration file changes.
        """
        # Convert to absolute path if it's not already
        dirname = os.path.abspath(self._path) or '.'
        if not os.path.exists(dirname):
            logging.error(f"Directory for config file does not exist: {dirname}")
            return

        self._observer.schedule(self, path=dirname, recursive=False)
        try:
            self._observer.start()
        except FileNotFoundError as e:
            logging.error(f"Failed to start observer: {e}")

    def _stop_watching_config(self):
        """
        Stop the Watchdog observer when the application is closing.
        """
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def on_modified(self, event):
        """
        Watchdog event handler for file modifications.
        """
        with self._lock:
            if event.src_path.endswith(self._path):
                new_hash = self._calculate_file_hash()
                if new_hash != self.config_file_hash:
                    logging.info("Configuration file content changed, reloading...")
                    self._reload_config()
                    self.config_file_hash = new_hash
                else:
                    logging.info("Configuration file metadata changed, no content change detected.")

    def get_app_config(self) -> AppConfig:
        """
        Get the current configuration.
        """
        with self._lock:
            return AppConfig(**self._config_json)
