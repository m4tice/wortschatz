"""
author: @GUU8HC
"""
#pylint: disable=import-outside-toplevel, line-too-long

from flask import Flask

from app.settings import DEBUG_MODE, USER_DB, SECRET_KEY, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SECURE, SESSION_PERMANENT, SESSION_COOKIE_SAMESITE

def create_app():
    """
    function to create application
    Issues:
        #2.c: Session Security
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = SESSION_COOKIE_SAMESITE
    app.config['SESSION_PERMANENT'] = SESSION_PERMANENT

    from app.home import home_bp
    app.register_blueprint(home_bp, url_prefix='/home')

    from app.authentication import authentication_bp
    app.register_blueprint(authentication_bp, url_prefix='/auth')

    return app
