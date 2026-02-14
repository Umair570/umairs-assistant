import sqlite3
from datetime import datetime
from config import Config
import os

class DBManager:
    def __init__(self):
        os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            raw_text TEXT,
            intent TEXT,
            status TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def log_command(self, text, intent, status):
        query = "INSERT INTO command_logs (timestamp, raw_text, intent, status) VALUES (?, ?, ?, ?)"
        self.conn.execute(query, (datetime.now(), text, intent, status))
        self.conn.commit()

    def close(self):
        self.conn.close()