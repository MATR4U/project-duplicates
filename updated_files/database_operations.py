import sqlite3
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseOperations:

    def __init__(self, db_name="duplicates.db"):
        self.conn = sqlite3.connect(db_name)
        self._initialize_db()

    def _initialize_db(self):
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS files (
                        hash TEXT PRIMARY KEY,
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

    def hash_exists_in_db(self, file_hash):
        """
        Check if a given hash already exists in the database.
        """
        with self.conn:
            result = self.conn.execute("SELECT 1 FROM files WHERE hash=?", (file_hash,)).fetchone()
            return bool(result)
        
    def write_to_db(self, data):
        try:
            with self.conn:
                self.conn.executemany(
                    "INSERT OR IGNORE INTO files (hash, path, size, modification_time, access_time, creation_time) VALUES (?, ?, ?, ?, ?, ?)",
                    data
                )
            logging.info(f"Inserted {len(data)} entries into the database.")
        except Exception as e:
            logging.error(f"Error writing to database: {str(e)}")

    def get_file_hash(self, filepath):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT hash FROM files WHERE path = ?", (filepath,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            logging.error(f"Error fetching file hash from database: {str(e)}")
            return None

    def cleanup_database(self, days_old=30):
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
            with self.conn:
                self.conn.execute("DELETE FROM files WHERE date_added < ?", (cutoff_date,))
            logging.info(f"Cleaned up entries older than {days_old} days from the database.")
        except Exception as e:
            logging.error(f"Error cleaning up database: {str(e)}")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed successfully.")
