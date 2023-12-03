import sqlite3
from sqlite3 import Cursor
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseOperationsDuplicates:
    """Class provides all database operations for the schema duplicates"""

    def __init__(self, cursor: Cursor):
        try:
            self._initialize_schema_duplicates(cursor)
            logging.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logging.error("Error initializing database: %s", e)
            raise

    def _initialize_schema_duplicates(self, cursor: Cursor):
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS duplicates (
                    original_id INTEGER,
                    duplicate_ids JSON,
                    PRIMARY KEY (original_id),
                    FOREIGN KEY (original_id) REFERENCES files (id) ON DELETE CASCADE
                )
            """)

    def fetch_duplicates(self, cursor: Cursor):
        try:
                cursor.execute("SELECT original_id, duplicate_ids FROM duplicates")
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error("Error fetching all duplicates: %s", e)
            raise

    def add_duplicates(self, cursor: Cursor, original_id, duplicate_ids):
        try:
            # Check if original_id already has an entry in the duplicates table
            cursor.execute("SELECT duplicate_ids FROM duplicates WHERE original_id = ?", (original_id,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                # Load the existing duplicate IDs and convert them to a set for uniqueness
                existing_duplicate_ids_set = set(json.loads(existing_entry[0]))
                
                # Convert the new duplicate IDs list to a set and combine it with the existing set
                new_duplicate_ids_set = existing_duplicate_ids_set.union(set(duplicate_ids))
                
                # Convert the combined set back to a list and JSON encode it for database update
                new_duplicate_ids_json = json.dumps(list(new_duplicate_ids_set))
                
                # Update the existing entry with new unique duplicate_ids
                cursor.execute("UPDATE duplicates SET duplicate_ids = ? WHERE original_id = ?", (new_duplicate_ids_json, original_id))
            else:
                # Insert new entry into duplicates table with the unique list of duplicate IDs
                cursor.execute("INSERT INTO duplicates (original_id, duplicate_ids) VALUES (?, ?)", (original_id, json.dumps(duplicate_ids)))

        except sqlite3.Error as e:
            logging.error("Error processing duplicates: %s", e)
            raise

    def remove_marked_deleted(self, cursor: Cursor, id):
        try:
            # Find all duplicate entries where this file ID is present
            cursor.execute("SELECT original_id, duplicate_ids FROM duplicates")
            duplicates = cursor.fetchall()

            for original_id, duplicate_ids_json in duplicates:
                duplicate_ids = json.loads(duplicate_ids_json)
                
                # If the file ID is in the duplicate IDs, remove it
                if id in duplicate_ids:
                    duplicate_ids.remove(id)

                    if duplicate_ids:  # If there are more duplicates, update the entry
                        updated_json = json.dumps(duplicate_ids)
                        cursor.execute("UPDATE duplicates SET duplicate_ids = ? WHERE original_id = ?", (updated_json, original_id))
                    else:  # If no more duplicates, delete the entry
                        cursor.execute("DELETE FROM duplicates WHERE original_id = ?", (original_id,))


        except sqlite3.Error as e:
            logging.error("Error processing duplicates: %s", e)
            raise

        

        
