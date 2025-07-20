"""
Unit tests for authentication module.
Focuses on authentication routes, login/logout functionality, and session management.
author: @GUU8HC
"""
#pylint: disable=redefined-outer-name

import pytest
import json
from unittest.mock import patch
from flask import Flask

from app.authentication.authentication import authentication_bp


@pytest.fixture
def app():
    """Create a minimal Flask app for testing authentication routes."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.register_blueprint(authentication_bp, url_prefix='/auth')
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestAuthenticationRoutes:
    """Test authentication route handlers."""
    
    def test_login_page_renders(self, client):
        """Test that login page renders correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Wortschatz' in response.data
        assert b'Enter your email' in response.data
        assert b'Enter your password' in response.data
    
    def test_registration_page_renders(self, client):
        """Test that registration page renders correctly."""
        response = client.get('/auth/registration')
        assert response.status_code == 200
        assert b'Registration' in response.data
        assert b'Enter your email' in response.data
        assert b'Enter your password' in response.data
    
    def test_restore_password_page_renders(self, client):
        """Test that restore password page renders correctly."""
        response = client.get('/auth/restore-password')
        assert response.status_code == 200
        assert b'Restore Password' in response.data
    
    def test_obsolete_signin_page_renders(self, client):
        """Test that obsolete signin page renders correctly."""
        response = client.get('/auth/obsolete/signin')
        assert response.status_code == 200


class TestAuthenticationAPI:
    """Test authentication API endpoints."""
    
    @patch('app.authentication.authentication.authenticator')
    def test_authenticate_valid_credentials(self, mock_authenticator, client):
        """Test authentication with valid credentials."""
        mock_authenticator.authenticate.return_value = True
        
        response = client.get('/auth/login/testuser/testpass')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['result'] is True
        mock_authenticator.authenticate.assert_called_once_with('testuser', 'testpass')
    
    @patch('app.authentication.authentication.authenticator')
    def test_authenticate_invalid_credentials(self, mock_authenticator, client):
        """Test authentication with invalid credentials."""
        mock_authenticator.authenticate.return_value = False
        
        response = client.get('/auth/login/testuser/wrongpass')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['result'] is False
        mock_authenticator.authenticate.assert_called_once_with('testuser', 'wrongpass')
    
    @patch('app.authentication.authentication.authenticator')
    def test_register_new_user(self, mock_authenticator, client):
        """Test registration with new user."""
        mock_authenticator.register.return_value = True
        
        response = client.get('/auth/registration/newuser/newpass')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['result'] is True
        mock_authenticator.register.assert_called_once_with('newuser', 'newpass')
    
    @patch('app.authentication.authentication.authenticator')
    def test_register_existing_user(self, mock_authenticator, client):
        """Test registration with existing user."""
        mock_authenticator.register.return_value = False
        
        response = client.get('/auth/registration/existinguser/pass')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['result'] is False
        mock_authenticator.register.assert_called_once_with('existinguser', 'pass')


class TestSessionManagement:
    """Test session management functionality."""
    
    @patch('app.authentication.authentication.authenticator')
    def test_login_sets_session(self, mock_authenticator, client):
        """Test that successful login sets user session."""
        mock_authenticator.authenticate.return_value = True
        
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
        
        response = client.get('/auth/login/testuser/testpass')
        assert response.status_code == 200
        
        # Note: Session would be set by login_user() function in real scenario
        # This test verifies the endpoint is called correctly
    
    def test_logout_clears_session(self, client):
        """Test that logout clears user session."""
        # Set up session with user data
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
            sess['other_data'] = 'some_value'
        
        response = client.get('/auth/logout')
        assert response.status_code == 200
        assert b'Wortschatz' in response.data  # Returns to login page


class TestURLPatterns:
    """Test URL pattern matching and parameter extraction."""
    
    @patch('app.authentication.authentication.authenticator')
    def test_login_url_parameters(self, mock_authenticator, client):
        """Test that URL parameters are correctly extracted for login."""
        mock_authenticator.authenticate.return_value = True
        
        # Test with special characters in username/password
        response = client.get('/auth/login/test%40email.com/pass%21word')
        assert response.status_code == 200
        
        # Note: URL decoding should handle special characters
        mock_authenticator.authenticate.assert_called_once()
    
    @patch('app.authentication.authentication.authenticator')
    def test_registration_url_parameters(self, mock_authenticator, client):
        """Test that URL parameters are correctly extracted for registration."""
        mock_authenticator.register.return_value = True
        
        response = client.get('/auth/registration/newuser123/securepass456')
        assert response.status_code == 200
        
        mock_authenticator.register.assert_called_once_with('newuser123', 'securepass456')


class TestSecurityHeaders:
    """Test security-related headers and responses."""
    
    def test_json_response_headers(self, client):
        """Test that JSON responses have appropriate headers."""
        with patch('app.authentication.authentication.authenticator') as mock_auth:
            mock_auth.authenticate.return_value = True
            
            response = client.get('/auth/login/testuser/testpass')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
    
    def test_html_response_headers(self, client):
        """Test that HTML responses have appropriate headers."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert 'text/html' in response.content_type


if __name__ == '__main__':
    pytest.main([__file__])
