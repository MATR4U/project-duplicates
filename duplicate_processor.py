import os
import logging
from database_operations import DatabaseOperations
from file_operations import FileOperations
import json
from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DuplicateProcessor:
    def __init__(self, directory, db_name="duplicates.db"):
        with open('config.json', 'r') as file:
            self.config = json.load(file)
        self.directory = directory
        self.db_operations = DatabaseOperations(db_name)
        self.file_operations = FileOperations()

    @staticmethod
    def load_config():
        """Load configuration from config.json."""
        try:
            with open('config.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            return {}

    def _get_filepaths(self):
        # Using a generator to lazily load file paths
        for dirpath, _, filenames in os.walk(self.directory):
            for filename in filenames:
                yield os.path.join(dirpath, filename)

    def _is_new_or_modified(self, filepath):
        # Check if file is new or has been modified since the last scan
        current_hash = self.file_operations.hash_file(filepath)
        stored_hash = self.db_operations.get_file_hash(filepath)
        return stored_hash is None or stored_hash != current_hash

    def find_duplicates(self):
        file_hashes = set()
        duplicates = {}
        
        # Parallelizing the hashing process
        with ProcessPoolExecutor() as executor:
            for filepath in self._get_filepaths():
                if not self._is_new_or_modified(filepath):
                    continue

                file_hash = self.file_operations.hash_file(filepath)
                if file_hash in file_hashes:
                    duplicates.setdefault(file_hash, []).append(filepath)
                else:
                    file_hashes.add(file_hash)
        return duplicates

    def process_duplicates(self):
        logging.info("Processing duplicates...")
        
        try:
            duplicates = self.find_duplicates()
            
            # Convert duplicates into a format suitable for database insertion
            data_to_insert = []
            for file_hash, filepaths in duplicates.items():
                for filepath in filepaths:
                    if not self.db_operations.hash_exists_in_db(file_hash):
                        metadata = self.file_operations.get_file_metadata(filepath)
                        data_to_insert.append((file_hash, filepath) + metadata)
                    else:
                        logging.info(f"Duplicate hash {file_hash} for file {filepath} already exists in the database. Skipping.")
            
            # Write to database in batches using the batch size from the configuration file
            batch_size = self.config.get("batch_size", 100)  # Default to 100 if not in config
            for i in range(0, len(data_to_insert), batch_size):
                self.db_operations.write_to_db(data_to_insert[i:i+batch_size])
            
            logging.info(f"Processed {len(data_to_insert)} duplicate entries.")

        except Exception as e:
            logging.error(f"Error processing duplicates: {str(e)}")

    def process_duplicates(self):
        logging.info("Processing duplicates...")
        try:
            duplicates = self.find_duplicates()
            data_to_insert = [(file_hash, filepath) + self.file_operations.get_file_metadata(filepath) 
                              for file_hash, filepaths in duplicates.items() 
                              for filepath in filepaths]
            batch_size = self.config.get("batch_size", 100)
            for i in range(0, len(data_to_insert), batch_size):
                self.db_operations.write_to_db(data_to_insert[i:i+batch_size])
            logging.info(f"Processed {len(data_to_insert)} duplicate entries.")
        except Exception as e:
            logging.error(f"Error processing duplicates: {str(e)}")

    def get_duplicates_summary(self):
        duplicates = self.db_operations.fetch_duplicates()

        # Grouping by hash
        grouped_duplicates = {}
        for entry in duplicates:
            hash_value = entry[0]
            path = entry[1]
            if hash_value not in grouped_duplicates:
                grouped_duplicates[hash_value] = []
            grouped_duplicates[hash_value].append(path)

        # Creating the summary
        summary = "Duplicate Files Summary:\n"
        for hash_value, paths in grouped_duplicates.items():
            summary += f"Hash: {hash_value}, Paths: {', '.join(paths)}\n"

        logging.info(summary)
        return summary

    def move_confirmed_duplicates(self, destination_directory):
        duplicates = self.db_operations.fetch_duplicates()
        file_paths = [duplicate[1] for duplicate in duplicates]
        self.file_operations.process_and_move_files(file_paths, destination_directory)