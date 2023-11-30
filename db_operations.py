import sqlite3
import logging
import datetime
import json
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseOperations:

    def __init__(self, db_name="duplicates.db"):
        self.db_name = db_name
        self.conn = self._open_connection(db_name)
        self._initialize_schema_files()
        self._initialize_schema_duplicates()

    def _initialize_schema_files(self):
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hash TEXT,
                        path TEXT,
                        size INTEGER,
                        modification_time REAL,
                        access_time REAL,
                        creation_time REAL,
                        date_added TEXT DEFAULT CURRENT_TIMESTAMP,
                        marked INTEGER DEFAULT 0
                    )
                """)

            logging.info("Database initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")

    def _initialize_schema_duplicates(self):
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS duplicates (
                        original_id INTEGER,
                        duplicate_ids JSON,
                        PRIMARY KEY (original_id),
                        FOREIGN KEY (original_id) REFERENCES files (id) ON DELETE CASCADE
                    )
                """)

            logging.info("Database initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")

    def _open_connection(self, db_name):
        """Establish a database connection."""
        try:
            return sqlite3.connect(db_name)
        except Exception as e:
            logging.error(f"Error connecting to the database: {str(e)}")
            return None

    def _close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

        logging.info("Database connection closed successfully.")

    def fetchall(self):
        """fetch all files"""
        if self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT id, hash, creation_time FROM files")
            all_files = cur.fetchall()
            return all_files
        
    def processDuplicates(self, original_id, duplicate_ids):
        if self.conn:
            cur = self.conn.cursor()
            # Check if original_id already has an entry in the duplicates table
            cur.execute("SELECT duplicate_ids FROM duplicates WHERE original_id = ?", (original_id,))
            existing_entry = cur.fetchone()

            if existing_entry:
                # Load the existing duplicate IDs and convert them to a set for uniqueness
                existing_duplicate_ids_set = set(json.loads(existing_entry[0]))
                
                # Convert the new duplicate IDs list to a set and combine it with the existing set
                new_duplicate_ids_set = existing_duplicate_ids_set.union(set(duplicate_ids))
                
                # Convert the combined set back to a list and JSON encode it for database update
                new_duplicate_ids_json = json.dumps(list(new_duplicate_ids_set))
                
                # Update the existing entry with new unique duplicate_ids
                cur.execute("UPDATE duplicates SET duplicate_ids = ? WHERE original_id = ?", (new_duplicate_ids_json, original_id))
            else:
                # Insert new entry into duplicates table with the unique list of duplicate IDs
                cur.execute("INSERT INTO duplicates (original_id, duplicate_ids) VALUES (?, ?)", (original_id, json.dumps(duplicate_ids)))

            self.conn.commit()

    def path_exists_in_db(self, filepath):
        # Check if the file path exists in the database
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT 1 FROM files WHERE path = ?", (filepath,))
            return cur.fetchone() is not None
    
    def get_existing_paths(self):
        """Retrieve a set of all file paths that are currently in the database."""
        try:
            with self.conn:  # Make sure you have a connection open to the database
                cur = self.conn.cursor()
                cur.execute("SELECT path FROM files")
                paths = cur.fetchall()  # This will get all paths as a list of tuples
                return set(path[0] for path in paths)  # Convert to a set of strings
        except Exception as e:
            logging.error(f"Error retrieving existing paths from the database: {e}")
            # Handle the exception as needed, possibly re-raise or return an empty set
            return set()
    
    def write_files_to_db_batch(self, file_data_list):
        """Insert multiple file data entries into the database."""
        
        query = """
            INSERT INTO files (hash, path, size, modification_time, access_time, creation_time)
            VALUES (:hash, :path, :size, :modification_time, :access_time, :creation_time)
        """
        try:
            with self.conn:
                cur = self.conn.cursor()
                cur.executemany(query, file_data_list)
                self.conn.commit()
                #logging.info(f"Batch of {len(file_data_list)} files inserted into the database.")
        except Exception as e:
            logging.error(f"Error inserting batch into database: {e}")
            raise

    def fetch_originals(self):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT f.id, f.path as original_path, d.duplicate_ids
                FROM files f
                INNER JOIN duplicates d ON f.id = d.original_id
                WHERE f.marked = 0
            """)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return []
        
    def get_duplicates(self):
        """
        Fetches and prints a summary of the original files and their duplicates.
        
        :param cursor: A sqlite3 cursor object.
        """
        try:
            originals = self.fetch_originals()
            originals_and_duplicates = {}

            for original_id, original_path, duplicate_ids_json in originals:
                # Decode the JSON list of duplicate IDs
                duplicate_ids = json.loads(duplicate_ids_json)

                # Fetch the paths for each duplicate ID
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT id, path, creation_time
                    FROM files
                    WHERE id IN ({0})
                """.format(",".join("?" for _ in duplicate_ids)), duplicate_ids)

                # Fetch the results
                duplicates = cursor.fetchall()

                # Build a set of tuples (duplicate_id, duplicate_path) for the duplicates
                duplicates_set = {(dup_id, dup_path, create_time) for dup_id, dup_path, create_time in duplicates}

                # Map the original path to its duplicates
                originals_and_duplicates[original_path] = duplicates_set

            return originals_and_duplicates

        except Exception as e:
            print(f"An error occurred while fetching duplicates summary: {e}")

    #TODO improve by do not DELETE moved files
    def remove_duplicate_entry(self, duplicate_id):
        try:
            with self.conn:
                cur = self.conn.cursor()

                # Delete the duplicate entry from the files table
                cur.execute("DELETE FROM files WHERE id = ?", (duplicate_id,))

                # Update the duplicates table
                cur.execute("SELECT original_id, duplicate_ids FROM duplicates")
                for original_id, duplicate_ids_json in cur.fetchall():
                    duplicate_ids = json.loads(duplicate_ids_json)
                    if duplicate_id in duplicate_ids:
                        duplicate_ids.remove(duplicate_id)
                        if duplicate_ids:  # If there are more duplicates, update the entry
                            cur.execute("UPDATE duplicates SET duplicate_ids = ? WHERE original_id = ?", (json.dumps(duplicate_ids), original_id))
                        else:  # If no more duplicates, delete the entry
                            cur.execute("DELETE FROM duplicates WHERE original_id = ?", (original_id))
                        
        except sqlite3.IntegrityError as ie:
            print("Integrity error occurred:", ie)
        except sqlite3.Error as e:
            print("Database error occurred:", e)

    def remove_original_entry_if_no_duplicates(self, original_path):
        with self.conn:
            cur = self.conn.cursor()
            # Select the original file's ID based on its path
            cur.execute("SELECT id FROM files WHERE path = ?", (original_path,))
            original_id = cur.fetchone()[0]
            # Check if the original file has any duplicates left
            cur.execute("SELECT COUNT(*) FROM duplicates WHERE original_id = ?", (original_id,))
            if cur.fetchone()[0] == 0:
                # If no duplicates left, delete the original file from the files table
                cur.execute("DELETE FROM files WHERE id = ?", (original_id,))
            self.conn.commit()