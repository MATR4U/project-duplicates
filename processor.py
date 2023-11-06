import os
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from db_operations import DatabaseOperations
from file_operations import FileOperations
from utilities import Utilities

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Processor:
    def __init__(self, dataSourceDirectory, dataDestinationDir):
        database_name = Utilities.load_config()["database_name"]
        self.dataSourceDirectory=dataSourceDirectory
        self.dataDestinationDir=dataDestinationDir
        self.db_operations = DatabaseOperations(database_name)
        self.file_operations = FileOperations(dataSourceDirectory, dataDestinationDir)

    def _get_all_filepaths(self):
        # Initialize the progress bar
        progress_bar = tqdm(desc="Walking through directories", unit="dir")

        # Walk through the directory structure once and store all file paths
        filepaths = []
        for dirpath, _, filenames in os.walk(self.dataSourceDirectory):
            for filename in filenames:
                filepaths.append(os.path.join(dirpath, filename))
            progress_bar.update(1)  # Update progress for each directory

        progress_bar.close()
        return filepaths
    
    def process_duplicates(self):
        self.db_operations.process_all_files_for_duplicates()     

    def _move_confirmed_duplicates(self, confirmed_duplicates, destination_directory):
        return None
        #try:
        #    for file_hash, paths in confirmed_duplicates.items():
        #        for path in paths[1:]:  # Keeping the first item as original, moving the rest
        #            self.file_operations.move_file_with_metadata_preserved(path, destination_directory)
        #            logging.info(f"Moved duplicate {path} to {destination_directory}")
        #except Exception as e:
        #    logging.error(f"Error moving confirmed duplicates: {e}")

    def get_all_files_batch(self):
        logging.info("Storing all files into the database...")
        
        filepaths = list(self._get_all_filepaths())  # Make sure this is a list if not already
        batch_size = 100  # Adjust the batch size as needed
        batches = [filepaths[i:i + batch_size] for i in range(0, len(filepaths), batch_size)]

        for batch in tqdm(batches, desc="Storing files", unit="batch"):
            file_data_batch = []
            for filepath in batch:
                if not self.db_operations.path_exists_in_db(filepath):
                    file_data =  self.file_operations.get_file_metadata(filepath)
                    file_data_batch.append(file_data)

            # Insert the batch into the database
            self.db_operations.write_files_to_db_batch(file_data_batch)

        logging.info("Finished storing files into the database.")

    def get_all_files_batch_optimized(self):
        logging.info("Storing all files into the database...")

        filepaths = sorted(list(self._get_all_filepaths()))
        existing_paths = self.db_operations.get_existing_paths()

        # Define the batch size for database writes
        batch_size = 100  # Adjust this size as needed

        # Initialize a list to collect file data for the current batch
        current_batch = []
        total_written = 0  # Counter for the total number of files written to the database

        # Use ThreadPoolExecutor to parallelize the file data preparation
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Prepare a progress bar to track file processing
            progress_bar = tqdm(total=len(filepaths), desc="Processing files", unit="file")

            # Map the filepaths to future objects, and store them in a dictionary
            future_to_filepath = {executor.submit(FileOperations.get_file_metadata, filepath): filepath for filepath in filepaths}

            # Iterate over the future objects as they complete
            for future in as_completed(future_to_filepath):
                filepath = future_to_filepath[future]
                try:
                    data = future.result()
                    if filepath not in existing_paths:
                        current_batch.append(data)
                        if len(current_batch) >= batch_size:
                            # Write the current batch to the database
                            self.db_operations.write_files_to_db_batch(current_batch)
                            total_written += len(current_batch)  # Update the total written counter
                            current_batch = []  # Reset the batch list after writing
                except Exception as e:
                    logging.error(f"Error processing file {filepath}: {e}")

                # Update progress bar each time a future is completed
                progress_bar.update(1)

            # Make sure to write any remaining files that didn't make up a full batch
            if current_batch:
                self.db_operations.write_files_to_db_batch(current_batch)
                total_written += len(current_batch)

            progress_bar.close()

        logging.info(f"Finished storing files into the database. {total_written} new files were added.")
