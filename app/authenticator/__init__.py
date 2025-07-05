"""
author: @GUU8HC
"""

from app.database import user_db

from .authenticator import Authenticator

authenticator = Authenticator(user_db)
