import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from tqdm import tqdm
from src.core.db_operations import DatabaseOperations
from src.core.file_operations import FileOperations
from src.utils.utilities import Utilities

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Processor:
    """Class processess all operations for fils and database"""

    def __init__(self, dataSourceDirectory, dataDestinationDir):
        database_name = Utilities.load_config()["database_name"]
        self.dataSourceDirectory=dataSourceDirectory
        self.dataDestinationDir=dataDestinationDir
        self.db_operations = DatabaseOperations(database_name)
        self.file_operations = FileOperations()

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

    def add_duplicates(self):
        """
        Goes through all files in the database, identifies duplicates, and processes them using in-memory calculations.
        """
        # Step 1: Retrieve all file entries and store them in memory.
        all_files = self.db_operations.fetch_all_files()

        # Step 2: Group entries by their hash.
        files_by_hash = {}
        for file_id, file_hash, creation_time in all_files:
            if file_hash not in files_by_hash:
                files_by_hash[file_hash] = []
            files_by_hash[file_hash].append((file_id, creation_time))

        # Initialize the progress bar
        progress_bar = tqdm(total=len(files_by_hash), desc="Processing duplicates", unit="hash")

        # Step 3: Process each group to determine the original and duplicate files.
        for file_hash, files in files_by_hash.items():
            if len(files) > 1:
                # Sort the files by creation time to find the oldest file.
                files.sort(key=lambda x: x[1])
                original_id = files[0][0]
                duplicate_ids = [file_id for file_id, _ in files[1:]]

                # Step 4: Insert the duplicates into the duplicates table.
                self.db_operations.process_duplicates(original_id, duplicate_ids)

            # Update the progress bar
            progress_bar.update(1)

        # Finalize the progress bar
        progress_bar.close()

        print("Processed all files for duplicates in memory.")


    def add_files(self):
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
            future_to_filepath = {executor.submit(self.file_operations.get_file_metadata, filepath): filepath for filepath in filepaths}

            # Iterate over the future objects as they complete
            for future in as_completed(future_to_filepath):
                filepath = future_to_filepath[future]
                try:
                    data = future.result()
                    if filepath not in existing_paths:
                        current_batch.append(data)
                        if len(current_batch) >= batch_size:
                            # Write the current batch to the database
                            self.db_operations.add_files(current_batch)
                            total_written += len(current_batch)  # Update the total written counter
                            current_batch = []  # Reset the batch list after writing
                except Exception as e:
                    logging.error("Error processing file {filepath}: %s", e)

                # Update progress bar each time a future is completed
                progress_bar.update(1)

            # Make sure to write any remaining files that didn't make up a full batch
            if current_batch:
                self.db_operations.add_files(current_batch)
                total_written += len(current_batch)

            progress_bar.close()

        logging.info("Finished storing files into the database. %s new files were added.", total_written)

    def print_duplicates_summary(self):
        duplicates = self.db_operations.get_files_and_duplicates()

        # Print the paths of the duplicates
        if duplicates:
            for key, value in duplicates.items():
                for item in value:
                    print(f"{key}: {value}")

    def move_duplicates(self):
        duplicates = self.db_operations.get_files_and_duplicates()
        filter_keywords = [".DS_Store", "@__thumb"]

        for original_path, duplicate_list in duplicates.items():
            # Filter out unwanted files
            if any(keyword in original_path for keyword in filter_keywords):
                continue

            for duplicate in duplicate_list:
                duplicate_id, duplicate_path, creation_time = duplicate
                year = Utilities.extract_year_from_timestamp(creation_time)  # creation_time

                if not os.path.exists(duplicate_path):
                    logging.error("File not found: {duplicate_path}")
                    self.db_operations.process_deleted_files(duplicate_id)
                    self.db_operations.remove_duplicate_entry(duplicate_id)
                    continue

                # Create the target directory based on the year
                target_dir = os.path.join(self.dataDestinationDir, str(year))
                os.makedirs(target_dir, exist_ok=True)

                # Move the file
                target_path = os.path.join(target_dir, os.path.basename(duplicate_path))
                try:
                    shutil.copy2(duplicate_path, target_path)  # Copy with metadata
                    os.remove(duplicate_path)  # Remove the original file

                    # Remove the empty folder if applicable
                    folder_path = os.path.dirname(duplicate_path)
                    if not os.listdir(folder_path):
                        os.rmdir(folder_path)
                    
                    print(f"Moved File: {duplicate_path} -> {target_path}")
                except Exception as e:
                    logging.error("Error moving file {duplicate_path}: %s", e)
                    continue

                # Update the database
                #TODO does not remove the duplicate entry even if the file was already moved.
                self.db_operations.remove_duplicate_entry(duplicate_id)