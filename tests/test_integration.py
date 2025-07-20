"""
Integration tests for the complete Wortschatz application.
Tests the full application workflow from authentication to wortschatz functionality.
author: @GUU8HC
"""
#pylint: disable=redefined-outer-name

import pytest
import tempfile
import os
import sqlite3
from unittest.mock import patch

from app import create_app


class TestConfig:
    """Test configuration class"""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = False
    SESSION_COOKIE_SAMESITE = 'Lax'


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    db_fd, db_path = tempfile.mkstemp()
    
    # Create the test database with user table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE user (
            userid TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Insert a test user with known credentials
    from app.authenticator.authenticator import Authenticator
    from app.database.user import User
    
    user_db = User(db_path)
    auth = Authenticator(user_db)
    hashed_password = auth.hash_password('testpass123')
    
    cursor.execute("INSERT INTO user VALUES (?, ?, ?)", 
                   ('testuser', 'testuser', hashed_password))
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except (PermissionError, FileNotFoundError):
        # On Windows, database files might still be locked
        pass


@pytest.fixture
def app(temp_db):
    """Create and configure a test Flask application."""
    with patch('app.settings.USER_DB', temp_db):
        app = create_app()
        app.config.from_object(TestConfig)
        return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


class TestFullApplicationWorkflow:
    """Test complete application workflows."""
    
    def test_user_registration_and_login_workflow(self, client, temp_db):
        """Test complete user registration and login workflow."""
        username = 'newuser'
        password = 'newpass123'
        
        # 1. Visit home page
        response = client.get('/home/')
        assert response.status_code == 200
        assert b'Willkommen bei Wortschatz' in response.data
        
        # 2. Go to registration page
        response = client.get('/auth/registration')
        assert response.status_code == 200
        assert b'Registration' in response.data
        
        # 3. Register new user
        response = client.get(f'/auth/registration/{username}/{password}')
        assert response.status_code == 200
        
        # 4. Login with new credentials
        response = client.get(f'/auth/login/{username}/{password}')
        assert response.status_code == 200
        
        # 5. Access private home page
        response = client.get('/home/private')
        assert response.status_code == 200
        assert b'Welcome to the Private Homepage' in response.data
        
        # 6. Access wortschatz modes
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        assert b'Daily' in response.data
        
        # 7. Access wortschatz session
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        assert b'Welcome to Wortschatz session' in response.data
        
        # 8. Logout
        response = client.get('/auth/logout')
        assert response.status_code == 200
        
        # 9. Verify logout by trying to access protected page
        response = client.get('/home/private')
        assert response.status_code == 302  # Redirect to login
    
    def test_existing_user_login_workflow(self, client):
        """Test login workflow with existing user."""
        # Use the pre-created test user
        username = 'testuser'
        password = 'testpass123'
        
        # 1. Visit login page
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        # 2. Login with existing credentials
        response = client.get(f'/auth/login/{username}/{password}')
        assert response.status_code == 200
        
        # 3. Access protected content
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        
        # 4. Navigate between protected pages
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        
        response = client.get('/home/private')
        assert response.status_code == 200
    
    def test_authentication_failure_workflow(self, client):
        """Test workflow when authentication fails."""
        # 1. Try to login with wrong credentials
        response = client.get('/auth/login/wronguser/wrongpass')
        assert response.status_code == 200
        
        # 2. Try to access protected content
        response = client.get('/wortschatz/modes')
        assert response.status_code == 302  # Redirect to login
        
        response = client.get('/home/private')
        assert response.status_code == 302  # Redirect to login
    
    def test_session_management_workflow(self, client):
        """Test session management throughout application."""
        username = 'testuser'
        password = 'testpass123'
        
        # 1. Verify no initial session
        response = client.get('/home/private')
        assert response.status_code == 302
        
        # 2. Login and establish session
        response = client.get(f'/auth/login/{username}/{password}')
        assert response.status_code == 200
        
        # 3. Verify session works across multiple requests
        response = client.get('/home/private')
        assert response.status_code == 200
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        
        # 4. Logout and verify session is cleared
        response = client.get('/auth/logout')
        assert response.status_code == 200
        
        response = client.get('/home/private')
        assert response.status_code == 302


class TestApplicationSecurity:
    """Test security aspects of the application."""
    
    def test_unauthenticated_access_blocked(self, client):
        """Test that all protected routes block unauthenticated access."""
        protected_routes = [
            '/home/private',
            '/wortschatz/modes',
            '/wortschatz/session'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302, f"Route {route} should redirect unauthenticated users"
            assert '/auth/login' in response.location
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attacks."""
        # Try SQL injection in authentication
        malicious_input = "admin'; DROP TABLE user; --"
        
        response = client.get(f'/auth/login/{malicious_input}/password')
        assert response.status_code == 200
        
        # Should not affect database - try normal login after
        response = client.get('/auth/login/testuser/testpass123')
        assert response.status_code == 200
    
    def test_session_security(self, client):
        """Test session security measures."""
        username = 'testuser'
        password = 'testpass123'
        
        # Login
        response = client.get(f'/auth/login/{username}/{password}')
        assert response.status_code == 200
        
        # Check that session is properly isolated
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            original_user_id = sess['user_id']
        
        # Access protected content
        response = client.get('/home/private')
        assert response.status_code == 200
        
        # Verify session persistence
        with client.session_transaction() as sess:
            assert sess['user_id'] == original_user_id


class TestApplicationErrors:
    """Test error handling across the application."""
    
    def test_404_errors(self, client):
        """Test 404 error handling."""
        invalid_routes = [
            '/nonexistent',
            '/home/invalid',
            '/auth/invalid',
            '/wortschatz/invalid'
        ]
        
        for route in invalid_routes:
            response = client.get(route)
            assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP methods."""
        # These routes should only accept GET
        get_only_routes = [
            '/home/',
            '/auth/login',
            '/auth/registration'
        ]
        
        for route in get_only_routes:
            response = client.post(route)
            assert response.status_code == 405
    
    def test_authentication_with_invalid_credentials(self, client):
        """Test authentication with various invalid credential formats."""
        invalid_credentials = [
            ('', ''),
            ('validuser', ''),
            ('', 'validpass'),
            ('user with spaces', 'password'),
            ('user@email.com', 'pass'),
            ('verylongusername' * 10, 'password')
        ]
        
        for username, password in invalid_credentials:
            response = client.get(f'/auth/login/{username}/{password}')
            assert response.status_code == 200  # Should return response, not crash


class TestApplicationPerformance:
    """Test performance-related aspects."""
    
    def test_multiple_concurrent_sessions(self, client):
        """Test handling of multiple session operations."""
        # Simulate rapid session operations
        for i in range(10):
            response = client.get('/auth/login/testuser/testpass123')
            assert response.status_code == 200
            
            response = client.get('/home/private')
            assert response.status_code == 200
            
            response = client.get('/auth/logout')
            assert response.status_code == 200
    
    def test_database_operations_performance(self, client, temp_db):
        """Test that database operations complete in reasonable time."""
        import time
        
        # Register multiple users
        for i in range(5):
            start_time = time.time()
            response = client.get(f'/auth/registration/user{i}/pass{i}')
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 1.0  # Should complete within 1 second


class TestBlueprintIntegration:
    """Test integration between different blueprints."""
    
    def test_cross_blueprint_navigation(self, client):
        """Test navigation between different blueprint routes."""
        # Start from home
        response = client.get('/home/')
        assert response.status_code == 200
        
        # Go to authentication
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        # Login
        response = client.get('/auth/login/testuser/testpass123')
        assert response.status_code == 200
        
        # Go to private home
        response = client.get('/home/private')
        assert response.status_code == 200
        
        # Go to wortschatz
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        
        # Navigate within wortschatz
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        
        # Back to home
        response = client.get('/home/private')
        assert response.status_code == 200
        
        # Logout
        response = client.get('/auth/logout')
        assert response.status_code == 200
    
    def test_blueprint_url_prefixes(self, client):
        """Test that blueprint URL prefixes work correctly."""
        # Test home blueprint (prefix: /home)
        response = client.get('/home/')
        assert response.status_code == 200
        
        # Test auth blueprint (prefix: /auth)
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        # Test wortschatz blueprint (prefix: /wortschatz)
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200


class TestDataConsistency:
    """Test data consistency across the application."""
    
    def test_user_data_consistency(self, client, temp_db):
        """Test that user data remains consistent throughout the application."""
        username = 'consistencytest'
        password = 'testpass'
        
        # Register user
        response = client.get(f'/auth/registration/{username}/{password}')
        assert response.status_code == 200
        
        # Verify user can login immediately after registration
        response = client.get(f'/auth/login/{username}/{password}')
        assert response.status_code == 200
        
        # Verify user session is maintained
        response = client.get('/home/private')
        assert response.status_code == 200
        
        # Logout and verify user still exists
        response = client.get('/auth/logout')
        assert response.status_code == 200
        
        # Login again to verify user data persistence
        response = client.get(f'/auth/login/{username}/{password}')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])
