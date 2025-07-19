"""
author: @guu8hc
"""

from flask import render_template

from app.util import login_required
from app.util import get_git_branch

from . import wortschatz_bp


@wortschatz_bp.route('/modes')
@login_required
def modes():
    """
    Render the wortschatz page template.
    Returns:
        str: The rendered HTML of the home page.
    """
    return render_template('wortschatz/modes.html', gitv=get_git_branch())

@wortschatz_bp.route('/session')
@login_required
def session():
    """
    Render the session page template.
    Returns:
        str: The rendered HTML of the session page.
    """
    return render_template('wortschatz/session.html', gitv=get_git_branch())
