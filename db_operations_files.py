import sqlite3
from sqlite3 import Cursor
import logging
import datetime
import json
from tqdm import tqdm

logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseOperationsFiles:

    def __init__(self, cursor: Cursor):
        """
        Initializes the DatabaseOperationsFiles object, setting up the schema for the 'files' table.
        
        Args:
            cursor (Cursor): A SQLite cursor object to execute database operations.
        """

        try:
            self._initialize_schema_files(cursor)
            logging.info("Database schema files initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Error initializing database: {str(e)}")
            raise

    def _initialize_schema_files(self, cursor: Cursor):
        """
        Creates the 'files' table in the database if it does not exist.

        Args:
            cursor (Cursor): A SQLite cursor object to execute database operations.
        """

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT,
                    path TEXT,
                    size INTEGER,
                    modification_time REAL,
                    access_time REAL,
                    creation_time REAL,
                    date_added TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_deleted INTEGER DEFAULT 0
                )
            """)

    def fetch_files(self, cursor: Cursor):
        """
        Fetches all file records from the 'files' table in the database.

        Args:
            cursor (Cursor): A SQLite cursor object to execute database operations.

        Returns:
            list: A list of tuples, each containing file data.
        """

        try:
                cursor.execute("SELECT id, hash, creation_time FROM files")
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error fetching all files: {e}")
            raise

    def add_files(self, cursor: Cursor, file_data_list):
        """
        Inserts multiple file data entries into the 'files' table in the database.

        Args:
            cursor (Cursor): A SQLite cursor object to execute database operations.
            file_data_list (list): A list of file data tuples to be added to the database.
        """

        query = """
            INSERT INTO files (hash, path, size, modification_time, access_time, creation_time)
            VALUES (:hash, :path, :size, :modification_time, :access_time, :creation_time)
        """
        try:
                cursor.executemany(query, file_data_list)
                logging.info(f"Batch of {len(file_data_list)} files inserted into the database.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting batch into database: {e}")
            raise

    def get_existing_paths(self, cursor: Cursor):

        """
        Inserts multiple file data entries into the 'files' table in the database.

        Args:
            cursor (Cursor): A SQLite cursor object to execute database operations.
            file_data_list (list): A list of file data tuples to be added to the database.
        """
                
        try:
                cursor.execute("SELECT path FROM files")
                paths = cursor.fetchall()  # This will get all paths as a list of tuples
                return set(path[0] for path in paths)  # Convert to a set of strings
        except Exception as e:
            logging.error(f"Error retrieving existing paths from the database: {e}")
            # Handle the exception as needed, possibly re-raise or return an empty set
            return set()
        
    def mark_as_deleted(self, cursor: Cursor, file_id):
        """
        Marks a file entry as deleted in the 'files' table in the database.

        Args:
            cursor (Cursor): A SQLite cursor object to execute database operations.
            file_id (int): The ID of the file to be marked as deleted.
        """
        try:
                cursor.execute("UPDATE files SET is_deleted = 1 WHERE id = ?", (file_id,))
                logging.info(f"File with ID {file_id} marked as deleted.")
        except sqlite3.Error as e:
            logging.error(f"Error marking file as deleted: {e}")
            raise