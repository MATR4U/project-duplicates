import sqlite3
import logging
import json
from database.operations.db_operations_files import DatabaseOperationsFiles
from database.operations.db_operations_duplicates import DatabaseOperationsDuplicates

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseOperations:
    """Class provides all database operations"""

    def __init__(self, db_name="duplicates.db"):
        """
        Initializes the DatabaseOperations object with a connection to the specified SQLite database.
        It also initializes two sub-classes for handling operations on 'files' and 'duplicates' tables.

        Args:
            db_name (str): Name of the SQLite database file.
        """

        try:
            self.conn = self._open_connection(db_name)
            self.db_operations_files = DatabaseOperationsFiles(self.conn.cursor())
            self.db_operations_duplicates = DatabaseOperationsDuplicates(self.conn.cursor())
            logging.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logging.error("Error initializing database: %s", str(e))
            raise

    def _open_connection(self, db_name):
        """
        Establishes and returns a connection to the SQLite database.

        Args:
            db_name (str): Name of the SQLite database file.

        Returns:
            sqlite3.Connection: A connection object to the SQLite database.
        """

        try:
            return sqlite3.connect(db_name)
        except sqlite3.Error as e:
            logging.error("Error connecting to the database: %s", str(e))
            raise

    def _close_connection(self):
        """
        Closes the database connection if it is open.
        """

        if self.conn and not self.conn.closed:
            self.conn.close()
            logging.info("Database connection closed successfully.")

    def get_existing_paths(self):
        """
        Fetches and returns existing file paths from the 'files' table in the database.

        Returns:
            list: A list of file paths.
        """

        return self.db_operations_files.get_existing_paths(self.conn.cursor())

    def fetch_all_files(self):
        """
        Retrieves all file records from the 'files' table in the database.

        Returns:
            list: A list of tuples, each containing file data.
        """

        return self.db_operations_files.fetch_files(self.conn.cursor())

    def add_files(self, file_data_list):
        """
        Adds a list of file data records to the 'files' table in the database.

        Args:
            file_data_list (list): A list of file data tuples to be added to the database.
        """

        return self.db_operations_files.add_files(self.conn.cursor(), file_data_list)

    def process_duplicates(self, original_id, duplicate_ids):
        """
        Processes and stores duplicate file information in the 'duplicates' table.

        Args:
            original_id (int): The ID of the original file.
            duplicate_ids (list): A list of duplicate file IDs.
        """

        return self.db_operations_duplicates.add_duplicates(self.conn.cursor(), original_id, duplicate_ids)

    def process_deleted_files(self, id):
        """
        Marks a file as deleted in the 'files' table and updates the 'duplicates' table
        to reflect this change.

        Args:
            id (int): The ID of the file to be marked as deleted.
        """

        self.db_operations_files.mark_as_deleted(self.conn.cursor(), id)
        self.db_operations_duplicates.remove_marked_deleted(self.conn.cursor(), id)

    def fetch_files_and_duplicate_json(self):
        """
        Fetches original files that are not marked as deleted and their associated duplicates
        from the database.

        Returns:
            list of tuples: Each tuple contains the original file ID, path, and a JSON string of duplicate IDs.
        """

        all_files = []

        try:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("""
                    SELECT f.id, f.path as original_path, d.duplicate_ids
                    FROM files f
                    INNER JOIN duplicates d ON f.id = d.original_id
                    WHERE f.is_deleted = 0
                """)
                all_files = cur.fetchall()

        except sqlite3.Error as e:
            logging.error("An error occurred: %s", e)
            # Depending on your application's requirements, you might want to re-raise the exception
            raise

        return all_files

    def get_files_and_duplicates(self):
        """
        Fetches and organizes a summary of the original files and their duplicates.
        This method processes and groups duplicate file information based on the original files.

        Returns:
            dict: A dictionary where each key is an original file path and its value is a set of tuples
            for its duplicate files (including ID, path, and creation time).
        """

        try:
            originals = self.fetch_files_and_duplicate_json()
            originals_and_duplicates = {}

            # Collect all duplicate IDs
            all_duplicate_ids = [dup_id for _, _, duplicate_ids_json in originals for dup_id in
                                 json.loads(duplicate_ids_json)]

            if all_duplicate_ids:
                # Fetch all paths for duplicate IDs in a single query
                cursor = self.conn.cursor()
                query = "SELECT id, path, creation_time FROM files WHERE id IN ({0})"
                query = query.format(",".join("?" * len(all_duplicate_ids)))
                cursor.execute(query, all_duplicate_ids)
                all_duplicates = cursor.fetchall()

                # Group duplicates by their original file
                duplicates_by_original = {original_id: [] for original_id, _, _ in originals}
                for dup_id, dup_path, create_time in all_duplicates:
                    for original_id, _, duplicate_ids_json in originals:
                        if dup_id in json.loads(duplicate_ids_json):
                            duplicates_by_original[original_id].append((dup_id, dup_path, create_time))

                # Map original paths to their duplicates
                for original_id, original_path, _ in originals:
                    originals_and_duplicates[original_path] = duplicates_by_original[original_id]

            return originals_and_duplicates

        except sqlite3.Error as e:
            logging.error("Database error occurred while fetching duplicates summary: %s", e)

    def remove_duplicate_entry(self, duplicate_id):
        """
        Removes an entry from the 'duplicates' table based on the duplicate file ID.
        If the file is marked as deleted in the 'files' table, it is also removed from the 'duplicates' table.

        Args:
            duplicate_id (int): The ID of the duplicate file to be removed.
        """

        try:
            with self.conn:
                cur = self.conn.cursor()

                # Check if the file is marked as deleted
                cur.execute("SELECT is_deleted FROM files WHERE id = ?", (duplicate_id,))
                result = cur.fetchone()
                if result and result[0] == 1:  # File is marked as deleted
                    # Update the duplicates table only for entries that contain this duplicate ID
                    cur.execute(
                        "SELECT original_id, duplicate_ids FROM duplicates WHERE json_extract(duplicate_ids, '$') LIKE ?",
                        ('%' + str(duplicate_id) + '%',))
                    for original_id, duplicate_ids_json in cur.fetchall():
                        duplicate_ids = json.loads(duplicate_ids_json)

                        # Remove the duplicate ID
                        if duplicate_id in duplicate_ids:
                            duplicate_ids.remove(duplicate_id)
                            if duplicate_ids:  # If there are more duplicates, update the entry
                                cur.execute("UPDATE duplicates SET duplicate_ids = ? WHERE original_id = ?",
                                            (json.dumps(duplicate_ids), original_id))
                            else:  # If no more duplicates, delete the entry
                                cur.execute("DELETE FROM duplicates WHERE original_id = ?", (original_id,))
                # Else, do nothing if the file is not marked as deleted

        except sqlite3.IntegrityError as e:
            logging.error("Integrity error occurred: %s", {e})
        except sqlite3.Error as e:
            logging.error("Database error occurred: %s", {e})
