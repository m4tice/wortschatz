"""
author: @GUU8HC
"""

from app.settings import USER_DB, DEEN_DB

from .user import User
from .wortschatz import Worschatz

user_db = User(USER_DB)
deen_db = Worschatz(DEEN_DB)
