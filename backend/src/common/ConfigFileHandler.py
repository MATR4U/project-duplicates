import json
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ConfigFileHandler(FileSystemEventHandler):

    CONFIG_FILE = 'config.json'
    _instance = None
    _config = None  # Class attribute to store config data
    _observer = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigFileHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_file=None):
        self._config = self._load_config(config_file)
        self._observer = None
        self._start_watching_config()


    def _load_config(self, config_file=None):
        if self._config is None:
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

    def reload_config(self):
        self._load_config()

    def _start_watching_config(self):
        self.observer = Observer()
        self.observer.schedule(ConfigFileHandler(self), path='.', recursive=False)
        self.observer.start()

    # Call this method when your application is closing
    def _stop_watching_config(self):
        if self._observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    def _on_modified(self, event):
        if event.src_path == event.src_path.endswith(self.CONFIG_FILE):
            logging.info("Configuration file changed, reloading...")
            self.config.reload_config()

    def getConfig(self):
        return self._config
