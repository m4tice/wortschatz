"""
author: @GUU8HC
"""

DEBUG_MODE = True
GIT_BRANCH = True

# Path to the user database
USER_DB = "app/database/dbs/user.db"
DEEN_DB = "app/database/dbs/de-en.db"

SECRET_KEY = 'your_secret_key'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True only in production with HTTPS
SESSION_PERMANENT = False
SESSION_COOKIE_SAMESITE = 'Lax'  # Less restrictive than 'Strict', works better with Safari
