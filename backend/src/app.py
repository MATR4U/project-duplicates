import logging
from src.core.processor import Processor
from src.api.server import API
from src.utils.config import Config
from src.db.database import Database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class App:
    _instance = None  # Private class-level instance attribute
    _initialized = False
    _args = None

    def __new__(cls, args=None):
        if cls._instance is None:
            cls._args = args
            cls._instance = super(App, cls).__new__(cls)
        return cls._instance

    def __init__(self, args=None):
        self.processor = Processor()
        self.api = API()
        self.config = Config(self._args)
        self.db: Database = Database()
        self.db.initialize(self.config.get_database_url())
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'App':
        try:
            if not cls._instance:
                cls._instance = cls()
            return cls._instance
        except Exception as e:
            logging.error(f"Failed to get instance: {e}")
            return None
    
    def run_db(self):
            try:
                # Get the db instance from the Database class
                db = Database.get_instance()

                # Use the db instance to execute a query
                rows = db.execute("SELECT * FROM files")

                # Print the results
                for row in rows:
                    print(row)

            except Exception as e:
                print(f"An error occurred: {e}")

    # TODO Cleanup process
    def run_api(self):
        self.api.run()

    def run_cli(self):
        # TODO Cleanup process should stage the change into a new delete schema, movement of the files should be acknowledged.
        # csv file is exported including the to be deleted data
        # patterns = ['.@__thumb', '.thumbnails', '@eaDir', '.picasa.ini']
        # Utilities.process_items_with_pattern(dataSourceDir, patterns, dataDestinationDir, True)
        # self.processor.export_pattern_summary()

        # TODO if data is already in the database, first should be checked which of the data is still available
        # if data is not available mark is_deleted
        # if data is_deleted marked it should be removed from the duplication schema

        # the filesystem should be checked for new available data that is not yet in the database
        logging.info("Starting process store in database...")
        self.processor.add_files(self.config.get_source())
        # self.processor.export_files_summary()

        # the whole available database should be checked for any duplicates
        # duplicates should be added
        logging.info("Starting process find and mark duplicates...")
        self.processor.add_duplicates()
        # self.processor.export_duplicates_summary()
                
        # Wait for user confirmation to move duplicates
        # user_input = input("Do you want to move the duplicates to the target directory? (yes/no): ")
        # if user_input.lower() == "yes":
        #     self.processor.move_duplicates()
        logging.info("Duplicate processing completed.")
