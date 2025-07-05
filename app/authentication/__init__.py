"""
author: @GUU8HC
"""
#pylint: disable=line-too-long
#pylint: disable=wrong-import-position

from flask import Blueprint

authentication_bp = Blueprint('authentication', __name__, template_folder='templates', static_folder='static')

from . import authentication
