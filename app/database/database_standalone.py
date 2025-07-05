"""
author: @GUU8HC
test place for database
"""
#pylint: disable=wrong-import-position
#pylint: disable=line-too-long

import os
import sys

# Add the root directory of the project to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# This is executed only when the script is run directly
if __name__ == "__main__":
    from app.database import user_db

    print("[DEBUG] test_database.py: Testing database operations")
    print(f"[TEST] User GUU8HC existence in DB: {"guu8hc" == user_db.get_user_by_username('guu8hc')[1]}")
