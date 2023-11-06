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

    def process_all_files_for_duplicates(self):
        """
        Goes through all files in the database, identifies duplicates, inserts them into
        the duplicates table, and marks the duplicates in the files table.
        """
        try:
            with self.conn:
                cur = self.conn.cursor()
                
                # Get all unique hashes with more than one file associated
                cur.execute("""
                    SELECT hash
                    FROM files
                    GROUP BY hash
                    HAVING COUNT(hash) > 1
                """)
                all_hashes_with_duplicates = [row[0] for row in cur.fetchall()]

                # Initialize the progress bar
                progress_bar = tqdm(total=len(all_hashes_with_duplicates), desc="Processing duplicates", unit="hash")

                for file_hash in all_hashes_with_duplicates:
                    # Get the ID of the original file (the oldest file by creation time)
                    cur.execute("""
                        SELECT id
                        FROM files
                        WHERE hash = ?
                        ORDER BY creation_time ASC
                        LIMIT 1
                    """, (file_hash,))
                    original_id = cur.fetchone()[0]
                    
                    # Get the IDs of the duplicate files
                    cur.execute("""
                        SELECT id
                        FROM files
                        WHERE hash = ? AND id != ?
                        ORDER BY creation_time ASC
                    """, (file_hash, original_id))
                    duplicates = [row[0] for row in cur.fetchall()]
                    
                    # Insert into duplicates table
                    if duplicates:
                        cur.execute("""
                            INSERT INTO duplicates (original_id, duplicate_ids)
                            VALUES (?, ?)
                        """, (original_id, json.dumps(duplicates)))
                    
                    # Mark the duplicates in the files table
                    cur.executemany("""
                        UPDATE files
                        SET marked = 1
                        WHERE id = ?
                    """, [(dup_id,) for dup_id in duplicates])

                    # Update the progress bar
                    progress_bar.update(1)

                # Finalize the progress bar
                progress_bar.close()
                self.conn.commit()
                print(f"Processed all files for duplicates.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def hash_exists_in_db(self, file_hash):
        """
        Check if a given hash already exists in the database.
        """
        with self.conn:
            result = self.conn.execute("SELECT 1 FROM files WHERE hash=?", (file_hash,)).fetchone()
            return bool(result)

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
        
    def write_file_to_db(self, file_data):
        """Insert the file data into the database if the path does not exist."""
        try:
            with self.conn:
                cur = self.conn.cursor()
                # Check if the path already exists in the database
                if not self.path_exists_in_db(file_data[1]):
                    cur.execute("""
                        INSERT INTO files (hash, path, size, modification_time, access_time, creation_time)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, file_data)
                    self.conn.commit()
                    logging.info(f"File data for '{file_data[1]}' has been inserted into the database.")
                else:
                    logging.info(f"File '{file_data[1]}' already exists in the database. No insertion made.")
        except Exception as e:
            logging.error(f"Error writing file to database: {e}")
            raise

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

    def get_file_hash(self, filepath):
        try:
            self.conn.cursor().execute("SELECT hash FROM files WHERE path = ?", (filepath,))
            result = self.conn.cursor().fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            logging.error(f"Error fetching file hash from database: {str(e)}")
            return None

    def get_all_paths_by_hash(self, file_hash):
        self.conn.cursor().execute("""
            SELECT path FROM file_paths WHERE hash = ?
        """, (file_hash,))
        return self.conn.cursor().fetchall()

    def add_file_hash_and_path(self, file_hash, file_data, filepath):
        # Check if the hash already exists in file_hashes
        if not self.hash_exists_in_db(file_hash):
            # Insert into file_hashes if not exist
            self.conn.cursor().execute("""
                INSERT INTO file_hashes (hash, size, mtime, atime, ctime)
                VALUES (?, ?, ?, ?, ?)
            """, (file_hash,) + file_data)
        
        # Insert into file_paths
        try:
            self.conn.cursor().execute("""
                INSERT INTO file_paths (hash, path)
                VALUES (?, ?)
            """, (file_hash, filepath))
        except sqlite3.IntegrityError:
            # If the path already exists, it's a duplicate; handle accordingly
            pass

        self.conn.commit()

    def hash_exists_in_db(self, file_hash):
        self.conn.cursor().execute("""
            SELECT 1 FROM file_hashes WHERE hash = ?
        """, (file_hash,))
        return  self.conn.cursor().fetchone() is not None
    
    def update_paths_for_hash(self, file_hash, updated_paths):
        self.conn.cursor().execute("UPDATE files SET paths = ? WHERE hash = ?", (updated_paths, file_hash))
        self.conn.commit()

    def cleanup_database(self, days_old=30):
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
            with self.conn:
                self.conn.execute("DELETE FROM files WHERE date_added < ?", (cutoff_date,))
            logging.info(f"Cleaned up entries older than {days_old} days from the database.")
        except Exception as e:
            logging.error(f"Error cleaning up database: {str(e)}")

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
    
    def fetch_duplicates(self):
        # Assuming that self.conn is a persistent connection managed outside this method.
        try:
            with self.conn:  # The connection context manager will handle transactions.
                self.conn.cursor().execute("""
                    SELECT hash, GROUP_CONCAT(path) 
                    FROM files 
                    WHERE marked = 0
                    GROUP BY hash
                    HAVING COUNT(hash) > 1
                """)
                duplicates = self.conn.cursor().fetchall()
                    
            # Process the results outside of the database transaction.
            duplicates_dict = {} # {hash_: paths.split(",") for hash_, paths in duplicates}
            for hash_, paths in duplicates:
                path_list = paths.split(",")
                duplicates_dict[hash_] = path_list
                # Log the duplicates found
                logging.info(f"Duplicate found: {hash_} with files: {path_list}")

            return duplicates_dict

        except sqlite3.Error as e:
            logging.error(f"Error fetching duplicates from database: {str(e)}")
            return {}

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
                    SELECT id, path
                    FROM files
                    WHERE id IN ({0})
                """.format(",".join("?" for _ in duplicate_ids)), duplicate_ids)

                # Fetch the results
                duplicates = cursor.fetchall()

                # Build a set of tuples (duplicate_id, duplicate_path) for the duplicates
                duplicates_set = {(dup_id, dup_path) for dup_id, dup_path in duplicates}

                # Map the original path to its duplicates
                originals_and_duplicates[original_path] = duplicates_set

            return originals_and_duplicates

        except Exception as e:
            print(f"An error occurred while fetching duplicates summary: {e}")