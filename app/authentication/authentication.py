"""
author: @GUU8HC
"""

from flask import render_template, jsonify

from app.authenticator import authenticator
from app.util import login_user, logout_user
from app.util import get_git_branch
from app.settings import DEBUG_MODE

from . import authentication_bp

@authentication_bp.route('/obsolete/signin')
def obsolete_signin():
    """
    route: /signin
    """
    return render_template('authentication/obsolete/signin.html')

@authentication_bp.route('/login')
def login():
    """
    route: /auth/login
    """
    return render_template('authentication/login.html', gitv=get_git_branch())

@authentication_bp.route('/login/<username>/<password>', methods=['GET'])
def authenticate(username, password):
    """
    route: /auth/login/<username>/<password>
    """
    login_user(username)
    result = authenticator.authenticate(username, password)

    if DEBUG_MODE:
        print(f"[DEBUG] authentication.py: Authentication result: {result}")

    return jsonify({'result': result})

@authentication_bp.route('/registration')
def registration():
    """
    route: /auth/registration
    """
    return render_template('authentication/registration.html', gitv=get_git_branch())

@authentication_bp.route('/registration/<username>/<password>', methods=['GET'])
def register(username, password):
    """
    route: /auth/registration/<username>/<password>
    """
    return jsonify({'result': authenticator.register(username, password)})

@authentication_bp.route('/restore-password')
def restore_password():
    """
    route: /auth/restore-password
    """
    return render_template('authentication/restore-password.html', gitv=get_git_branch())

@authentication_bp.route('/logout')
def logout():
    """
    route: /auth/logout
    """
    logout_user()
    return render_template('authentication/login.html')
