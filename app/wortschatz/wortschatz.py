"""
author: @guu8hc
"""

from flask import render_template

from app.util import login_required
from app.util import get_git_branch

from . import wortschatz_bp


@wortschatz_bp.route('/')
@login_required
def worschatz():
    """
    Render the wortschatz page template.
    Returns:
        str: The rendered HTML of the home page.
    """
    return render_template('wortschatz/wortschatz.html', gitv=get_git_branch())
