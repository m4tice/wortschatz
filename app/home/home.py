"""
author: @GUU8HC
"""

from flask import render_template

from app.util import login_required
from app.util import get_git_branch

from . import home_bp

@home_bp.route('/')
def home():
    """
    Render the home page template.
    Returns:
        str: The rendered HTML of the home page.
    """
    return render_template('home/home.html', gitv=get_git_branch())

@home_bp.route('/private')
@login_required
def home_private():
    """
    Render the home page template.
    Returns:
        str: The rendered HTML of the home page.
    """
    return render_template('home/home-private.html', gitv=get_git_branch())
