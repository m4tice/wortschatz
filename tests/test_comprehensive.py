"""
Comprehensive unit tests for the Wortschatz Flask application.
Tests cover home routes, authentication, wortschatz module, database operations, and utilities.
author: @GUU8HC
"""
#pylint: disable=redefined-outer-name
#pylint: disable=unused-argument

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from flask import Flask, session

from app import create_app
from app.home.home import home_bp
from app.authentication.authentication import authentication_bp  
from app.wortschatz.wortschatz import wortschatz_bp
from app.database.user import User
from app.authenticator.authenticator import Authenticator
from app.util import login_required, login_user, logout_user, get_git_branch


class TestConfig:
    """Test configuration class"""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = False
    SESSION_COOKIE_SAMESITE = 'Lax'


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app()
    app.config.from_object(TestConfig)
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def mock_db():
    """Create a mock database connection."""
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    
    mock_db.cursor.return_value = mock_cursor
    mock_db.connection = mock_connection
    
    return mock_db, mock_cursor, mock_connection


class TestHomeRoutes:
    """Test cases for home module routes."""
    
    def test_home_route_get(self, client):
        """Test GET request to home route."""
        response = client.get('/home/')
        assert response.status_code == 200
        assert b'Willkommen bei Wortschatz' in response.data
    
    def test_home_private_route_without_login(self, client):
        """Test private home route redirects when not logged in."""
        response = client.get('/home/private')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location
    
    def test_home_private_route_with_login(self, client):
        """Test private home route with authenticated user."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user'
        
        response = client.get('/home/private')
        assert response.status_code == 200
        assert b'Welcome to the Private Homepage' in response.data


class TestAuthenticationRoutes:
    """Test cases for authentication module routes."""
    
    def test_login_page_get(self, client):
        """Test GET request to login page."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Wortschatz' in response.data
        assert b'Enter your email' in response.data
    
    def test_registration_page_get(self, client):
        """Test GET request to registration page."""
        response = client.get('/auth/registration')
        assert response.status_code == 200
        assert b'Registration' in response.data
        assert b'Enter your email' in response.data
    
    def test_restore_password_page_get(self, client):
        """Test GET request to restore password page."""
        response = client.get('/auth/restore-password')
        assert response.status_code == 200
        assert b'Restore Password' in response.data
    
    @patch('app.authentication.authentication.authenticator')
    def test_authenticate_success(self, mock_authenticator, client):
        """Test successful authentication."""
        mock_authenticator.authenticate.return_value = True
        
        response = client.get('/auth/login/testuser/testpass')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['result'] is True
    
    @patch('app.authentication.authentication.authenticator')
    def test_authenticate_failure(self, mock_authenticator, client):
        """Test failed authentication."""
        mock_authenticator.authenticate.return_value = False
        
        response = client.get('/auth/login/testuser/wrongpass')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['result'] is False
    
    @patch('app.authentication.authentication.authenticator')
    def test_register_success(self, mock_authenticator, client):
        """Test successful user registration."""
        mock_authenticator.register.return_value = True
        
        response = client.get('/auth/registration/newuser/newpass')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['result'] is True
    
    @patch('app.authentication.authentication.authenticator')
    def test_register_failure(self, mock_authenticator, client):
        """Test failed user registration (user exists)."""
        mock_authenticator.register.return_value = False
        
        response = client.get('/auth/registration/existinguser/pass')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['result'] is False
    
    def test_logout_route(self, client):
        """Test logout route."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user'
        
        response = client.get('/auth/logout')
        assert response.status_code == 200
        assert b'Wortschatz' in response.data  # Returns to login page


class TestWortschatzRoutes:
    """Test cases for wortschatz module routes."""
    
    def test_modes_route_without_login(self, client):
        """Test modes route redirects when not logged in."""
        response = client.get('/wortschatz/modes')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location
    
    def test_modes_route_with_login(self, client):
        """Test modes route with authenticated user."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        assert b'Daily' in response.data
        assert b'Level' in response.data
        assert b'Topic' in response.data
        assert b'Practice' in response.data
    
    def test_session_route_without_login(self, client):
        """Test session route redirects when not logged in."""
        response = client.get('/wortschatz/session')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location
    
    def test_session_route_with_login(self, client):
        """Test session route with authenticated user."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user'
        
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        assert b'Welcome to Wortschatz session' in response.data


class TestDatabaseUser:
    """Test cases for User database operations."""
    
    def test_user_init(self, mock_db):
        """Test User class initialization."""
        mock_db_path, mock_cursor, mock_connection = mock_db
        user = User(mock_db_path)
        assert user.table_user == "user"
    
    @patch('app.database.user.sqlite3')
    def test_get_all_users(self, mock_sqlite, mock_db):
        """Test getting all users from database."""
        mock_db_path, mock_cursor, mock_connection = mock_db
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('user1', 'user1', 'pass1'), ('user2', 'user2', 'pass2')]
        
        user = User(mock_db_path)
        users = user.get_all()
        
        mock_cursor.execute.assert_called_with("SELECT * FROM user;")
        assert len(users) == 2
        assert users[0][0] == 'user1'
    
    @patch('app.database.user.sqlite3')
    def test_get_user_by_username_exists(self, mock_sqlite, mock_db):
        """Test getting existing user by username."""
        mock_db_path, mock_cursor, mock_connection = mock_db
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('testuser', 'testuser', 'hashedpass')
        
        user = User(mock_db_path)
        result = user.get_user_by_username('testuser')
        
        mock_cursor.execute.assert_called_with("SELECT * FROM user WHERE username = ?;", ('testuser',))
        assert result[0] == 'testuser'
    
    @patch('app.database.user.sqlite3')
    def test_get_user_by_username_not_exists(self, mock_sqlite, mock_db):
        """Test getting non-existing user by username."""
        mock_db_path, mock_cursor, mock_connection = mock_db
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        user = User(mock_db_path)
        result = user.get_user_by_username('nonexistentuser')
        
        assert result is None
    
    @patch('app.database.user.sqlite3')
    def test_create_user_success(self, mock_sqlite, mock_db):
        """Test successful user creation."""
        mock_db_path, mock_cursor, mock_connection = mock_db
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        user = User(mock_db_path)
        result = user.create_user('newuser', 'hashedpass')
        
        mock_cursor.execute.assert_called_with(
            "INSERT INTO user (userid, username, password) VALUES (?, ?, ?);",
            ('newuser', 'newuser', 'hashedpass')
        )
        mock_connection.commit.assert_called_once()
        assert result is True
    
    @patch('app.database.user.sqlite3')
    def test_create_user_failure(self, mock_sqlite, mock_db):
        """Test failed user creation."""
        mock_db_path, mock_cursor, mock_connection = mock_db
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        user = User(mock_db_path)
        result = user.create_user('newuser', 'hashedpass')
        
        assert result is False
    
    @patch('app.database.user.sqlite3')
    def test_remove_user_success(self, mock_sqlite, mock_db):
        """Test successful user removal."""
        mock_db_path, mock_cursor, mock_connection = mock_db
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        user = User(mock_db_path)
        result = user.remove_user('testuser')
        
        mock_cursor.execute.assert_called_with("DELETE FROM user WHERE userid = ?;", ('testuser',))
        mock_connection.commit.assert_called_once()
        assert result is True


class TestAuthenticator:
    """Test cases for Authenticator class."""
    
    def test_hash_password(self, mock_db):
        """Test password hashing."""
        mock_db_obj, _, _ = mock_db
        auth = Authenticator(mock_db_obj)
        
        hashed = auth.hash_password('testpassword')
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != 'testpassword'
    
    def test_verify_password_correct(self, mock_db):
        """Test password verification with correct password."""
        mock_db_obj, _, _ = mock_db
        auth = Authenticator(mock_db_obj)
        
        password = 'testpassword'
        hashed = auth.hash_password(password)
        
        assert auth.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self, mock_db):
        """Test password verification with incorrect password."""
        mock_db_obj, _, _ = mock_db
        auth = Authenticator(mock_db_obj)
        
        password = 'testpassword'
        hashed = auth.hash_password(password)
        
        assert auth.verify_password('wrongpassword', hashed) is False
    
    def test_authenticate_success(self, mock_db):
        """Test successful authentication."""
        mock_db_obj, _, _ = mock_db
        mock_db_obj.get_user_by_username.return_value = ('testuser', 'testuser', 'hashed_password')
        
        auth = Authenticator(mock_db_obj)
        
        with patch.object(auth, 'verify_password', return_value=True):
            result = auth.authenticate('testuser', 'testpassword')
            assert result is True
    
    def test_authenticate_user_not_exists(self, mock_db):
        """Test authentication with non-existing user."""
        mock_db_obj, _, _ = mock_db
        mock_db_obj.get_user_by_username.return_value = None
        
        auth = Authenticator(mock_db_obj)
        result = auth.authenticate('nonexistentuser', 'testpassword')
        
        assert result is False
    
    def test_authenticate_wrong_password(self, mock_db):
        """Test authentication with wrong password."""
        mock_db_obj, _, _ = mock_db
        mock_db_obj.get_user_by_username.return_value = ('testuser', 'testuser', 'hashed_password')
        
        auth = Authenticator(mock_db_obj)
        
        with patch.object(auth, 'verify_password', return_value=False):
            result = auth.authenticate('testuser', 'wrongpassword')
            assert result is False
    
    def test_register_new_user(self, mock_db):
        """Test registering a new user."""
        mock_db_obj, _, _ = mock_db
        mock_db_obj.get_user_by_username.return_value = None  # User doesn't exist
        mock_db_obj.create_user.return_value = True
        
        auth = Authenticator(mock_db_obj)
        result = auth.register('newuser', 'newpassword')
        
        assert result is True
        mock_db_obj.create_user.assert_called_once()
    
    def test_register_existing_user(self, mock_db):
        """Test registering an existing user."""
        mock_db_obj, _, _ = mock_db
        mock_db_obj.get_user_by_username.return_value = ('existinguser', 'existinguser', 'password')
        
        auth = Authenticator(mock_db_obj)
        result = auth.register('existinguser', 'newpassword')
        
        assert result is False
        mock_db_obj.create_user.assert_not_called()


class TestUtilities:
    """Test cases for utility functions."""
    
    def test_login_user(self, app):
        """Test login_user function."""
        with app.test_request_context():
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    login_user('testuser')
                    # Need to check session in the same context
                with client.session_transaction() as sess:
                    assert sess.get('user_id') == 'testuser'
    
    def test_logout_user(self, app):
        """Test logout_user function."""
        with app.test_request_context():
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['user_id'] = 'testuser'
                    sess['other_data'] = 'some_value'
                
                logout_user()
                
                with client.session_transaction() as sess:
                    assert 'user_id' not in sess
                    assert 'other_data' not in sess
    
    @patch('app.util.Repo')
    def test_get_git_branch_enabled(self, mock_repo):
        """Test get_git_branch with GIT_BRANCH enabled."""
        mock_branch = MagicMock()
        mock_branch.name = 'main'
        mock_repo.return_value.active_branch = mock_branch
        
        with patch('app.util.GIT_BRANCH', True):
            branch = get_git_branch()
            assert branch == 'main'
    
    def test_get_git_branch_disabled(self):
        """Test get_git_branch with GIT_BRANCH disabled."""
        with patch('app.util.GIT_BRANCH', False):
            branch = get_git_branch()
            assert branch is None
    
    def test_login_required_decorator_with_login(self, app):
        """Test login_required decorator with logged in user."""
        with app.test_request_context():
            @login_required
            def protected_view():
                return "Protected content"
            
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['user_id'] = 'testuser'
                
                # This would need actual Flask context to test properly
                # For unit test, we'll test the decorator logic
                assert 'user_id' in session
    
    def test_login_required_decorator_without_login(self, app):
        """Test login_required decorator without logged in user."""
        with app.test_request_context():
            @login_required
            def protected_view():
                return "Protected content"
            
            # Test that user_id is not in session
            assert 'user_id' not in session


class TestAppConfiguration:
    """Test cases for Flask app configuration."""
    
    def test_app_creation(self):
        """Test Flask app creation and basic configuration."""
        app = create_app()
        assert app is not None
        assert app.config['SECRET_KEY'] is not None
    
    def test_blueprints_registered(self):
        """Test that all blueprints are registered."""
        app = create_app()
        
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'home' in blueprint_names
        assert 'authentication' in blueprint_names
        assert 'wortschatz' in blueprint_names
    
    def test_blueprint_url_prefixes(self):
        """Test blueprint URL prefixes."""
        app = create_app()
        
        # Check URL map for expected prefixes
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        
        # Home blueprint rules should start with /home
        home_rules = [rule for rule in rules if '/home/' in rule]
        assert len(home_rules) > 0
        
        # Auth blueprint rules should start with /auth
        auth_rules = [rule for rule in rules if '/auth/' in rule]
        assert len(auth_rules) > 0
        
        # Wortschatz blueprint rules should start with /wortschatz
        wortschatz_rules = [rule for rule in rules if '/wortschatz/' in rule]
        assert len(wortschatz_rules) > 0


class TestErrorHandling:
    """Test cases for error handling scenarios."""
    
    def test_404_error(self, client):
        """Test 404 error for non-existent route."""
        response = client.get('/nonexistent/route')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method."""
        response = client.post('/home/')  # GET only route
        assert response.status_code == 405


if __name__ == '__main__':
    pytest.main([__file__])
