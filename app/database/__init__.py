"""
author: @GUU8HC
"""

from app.settings import USER_DB, DEEN_DB

from .user import User
from .wortschatz import Wortschatz

user_db = User(USER_DB)
deen_db = Wortschatz(DEEN_DB)
