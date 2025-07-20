"""
author: @GUU8HC
AI-generated test cases for the Home class in the home module.
"""
#pylint: disable=redefined-outer-name

import pytest
from flask import Flask
from app.home.home import home_bp
from app.authentication.authentication import authentication_bp


@pytest.fixture
def client():
    """
    Creates a Flask test client for the application.
    This function sets up a Flask application with the home blueprint registered
    and configures it for testing. It then yields a test client that can be used
    to simulate requests to the application.
    Yields:
        FlaskClient: A test client for the Flask application.
    """
    app = Flask(__name__)
    app.register_blueprint(home_bp)
    app.register_blueprint(authentication_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Test the home route."""
    response = client.get('/')
    assert response.status_code == 200

def test_login_route(client):
    """Test the login route."""
    response = client.get('/login')
    assert response.status_code == 200
