"""
author: @GUU8HC
"""
#pylint: disable=import-outside-toplevel

from app.settings import DEBUG_MODE

class DBInterface:
    """
    Interface for database operations
    """
    def __init__(self, db):
        """
        *.db initialization
        """
        import sqlite3

        self.db = db
        self.connection = None
        self.cursor = None

        if self.db is not None:

            if DEBUG_MODE:
                print(f"[DEBUG] db_interface.py: Connecting to {self.db}")

            self.connection = sqlite3.connect(self.db, check_same_thread=False)
            self.cursor = self.connection.cursor()
