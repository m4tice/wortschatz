"""
author: @guu8hc
"""

from functools import wraps
from flask import redirect, url_for, session
from git import Repo

from app.settings import GIT_BRANCH

def login_required(f):
    """
    Decorator to restrict access to authenticated users.
    Redirects to the login page if the user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if the user is logged in
            return redirect(url_for('authentication.signin'))  # Redirect to the login page
        return f(*args, **kwargs)
    return decorated_function

def login_user(user_id):
    """
    Log in the user by storing their user ID in the session.
    Args:
        user_id (str): The ID of the user to log in.
    """
    session['user_id'] = user_id  # Store the user ID in the session

def logout_user():
    """
    Log out the user by removing their user ID from the session.
    """
    session.clear()  # Clear the session to log out the user

def get_git_branch():
    """
    return name of current Git branch
    """
    return Repo('.').active_branch.name if GIT_BRANCH else None
