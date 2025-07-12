"""
author: @guu8hc
"""

from flask import Blueprint

wortschatz_bp = Blueprint('wortschatz', __name__, static_folder='static', template_folder='templates')

from . import wortschatz
