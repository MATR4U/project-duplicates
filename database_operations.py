import sqlite3
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseOperations:

    def __init__(self, db_name="duplicates.db"):
        self.db_name = db_name
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""
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

    def hash_exists_in_db(self, file_hash):
        with sqlite3.connect(self.db_name) as conn:
            result = conn.execute("SELECT 1 FROM files WHERE hash=?", (file_hash,)).fetchone()
            return bool(result)

    def write_to_db(self, data):
        with sqlite3.connect(self.db_name) as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO files (hash, path, size, modification_time, access_time, creation_time) VALUES (?, ?, ?, ?, ?, ?)",
                data
            )
        logging.info(f"Inserted {len(data)} entries into the database.")

    def get_file_hash(self, filepath):
        with sqlite3.connect(self.db_name) as conn:
            result = conn.execute("SELECT hash FROM files WHERE path = ?", (filepath,)).fetchone()
            return result[0] if result else None

    def cleanup_database(self, days_old=30):
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("DELETE FROM files WHERE date_added < ?", (cutoff_date,))
        logging.info(f"Cleaned up entries older than {days_old} days from the database.")

    def fetch_duplicates(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT hash, GROUP_CONCAT(path) 
                FROM files 
                WHERE marked = 0
                GROUP BY hash
                HAVING COUNT(hash) > 1
            """)
            duplicates = cur.fetchall()
            return {hash_: paths.split(",") for hash_, paths in duplicates}
