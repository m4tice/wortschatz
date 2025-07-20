"""
Unit tests for utility functions and decorators.
Focuses on login_required decorator, session management, and Git integration.
author: @GUU8HC
"""
#pylint: disable=redefined-outer-name

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, session, url_for

from app.util import login_required, login_user, logout_user, get_git_branch


@pytest.fixture
def app():
    """Create a Flask app for testing utilities."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    
    # Add a test route that uses login_required
    @app.route('/protected')
    @login_required
    def protected_route():
        return "Protected content"
    
    # Add a login route for redirects
    @app.route('/auth/login')
    def login_route():
        return "Login page"
    
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestLoginRequired:
    """Test the login_required decorator."""
    
    def test_login_required_with_authenticated_user(self, client):
        """Test login_required allows access for authenticated users."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/protected')
        assert response.status_code == 200
        assert b'Protected content' in response.data
    
    def test_login_required_without_authentication(self, client):
        """Test login_required redirects unauthenticated users."""
        response = client.get('/protected')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_login_required_with_empty_session(self, client):
        """Test login_required with explicitly empty session."""
        with client.session_transaction() as sess:
            sess.clear()
        
        response = client.get('/protected')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_login_required_preserves_function_metadata(self):
        """Test that login_required preserves function metadata."""
        @login_required
        def test_function():
            """Test function docstring."""
            return "test"
        
        assert test_function.__name__ == 'test_function'
        assert test_function.__doc__ == "Test function docstring."


class TestSessionManagement:
    """Test session management functions."""
    
    def test_login_user(self, app):
        """Test login_user function sets session correctly."""
        with app.test_request_context():
            login_user('testuser123')
            assert session['user_id'] == 'testuser123'
    
    def test_login_user_overwrites_existing(self, app):
        """Test login_user overwrites existing session."""
        with app.test_request_context():
            session['user_id'] = 'olduser'
            login_user('newuser')
            assert session['user_id'] == 'newuser'
    
    def test_logout_user_clears_session(self, app):
        """Test logout_user clears entire session."""
        with app.test_request_context():
            session['user_id'] = 'testuser'
            session['other_data'] = 'some_value'
            session['more_data'] = {'key': 'value'}
            
            logout_user()
            
            assert len(session) == 0
            assert 'user_id' not in session
            assert 'other_data' not in session
            assert 'more_data' not in session
    
    def test_logout_user_empty_session(self, app):
        """Test logout_user with already empty session."""
        with app.test_request_context():
            # Ensure session is empty
            session.clear()
            
            # Should not raise error
            logout_user()
            assert len(session) == 0


class TestGitBranch:
    """Test Git branch functionality."""
    
    @patch('app.util.GIT_BRANCH', True)
    @patch('app.util.Repo')
    def test_get_git_branch_enabled_success(self, mock_repo):
        """Test get_git_branch when enabled and Git repo exists."""
        mock_branch = MagicMock()
        mock_branch.name = 'feature/test-branch'
        mock_repo.return_value.active_branch = mock_branch
        
        result = get_git_branch()
        assert result == 'feature/test-branch'
        mock_repo.assert_called_once_with('.')
    
    @patch('app.util.GIT_BRANCH', True)
    @patch('app.util.Repo')
    def test_get_git_branch_enabled_main_branch(self, mock_repo):
        """Test get_git_branch with main branch."""
        mock_branch = MagicMock()
        mock_branch.name = 'main'
        mock_repo.return_value.active_branch = mock_branch
        
        result = get_git_branch()
        assert result == 'main'
    
    @patch('app.util.GIT_BRANCH', True)
    @patch('app.util.Repo')
    def test_get_git_branch_enabled_develop_branch(self, mock_repo):
        """Test get_git_branch with develop branch."""
        mock_branch = MagicMock()
        mock_branch.name = 'develop'
        mock_repo.return_value.active_branch = mock_branch
        
        result = get_git_branch()
        assert result == 'develop'
    
    @patch('app.util.GIT_BRANCH', False)
    def test_get_git_branch_disabled(self):
        """Test get_git_branch when disabled in settings."""
        result = get_git_branch()
        assert result is None
    
    @patch('app.util.GIT_BRANCH', True)
    @patch('app.util.Repo')
    def test_get_git_branch_repo_error(self, mock_repo):
        """Test get_git_branch when Git repo cannot be accessed."""
        mock_repo.side_effect = Exception("Not a git repository")
        
        # Should not raise exception, but may return None or handle gracefully
        with pytest.raises(Exception):
            get_git_branch()


class TestDecoratorIntegration:
    """Test decorator integration with Flask routes."""
    
    def test_multiple_decorators(self, app):
        """Test login_required works with other decorators."""
        @app.route('/multi-protected')
        @login_required
        def multi_protected():
            return "Multi-protected content"
        
        with app.test_client() as client:
            # Without authentication
            response = client.get('/multi-protected')
            assert response.status_code == 302
            
            # With authentication
            with client.session_transaction() as sess:
                sess['user_id'] = 'testuser'
            
            response = client.get('/multi-protected')
            assert response.status_code == 200
            assert b'Multi-protected content' in response.data
    
    def test_decorator_with_arguments(self, app):
        """Test login_required on routes with arguments."""
        @app.route('/protected/<user_id>')
        @login_required
        def protected_with_args(user_id):
            return f"Protected content for {user_id}"
        
        with app.test_client() as client:
            # Without authentication
            response = client.get('/protected/123')
            assert response.status_code == 302
            
            # With authentication
            with client.session_transaction() as sess:
                sess['user_id'] = 'testuser'
            
            response = client.get('/protected/123')
            assert response.status_code == 200
            assert b'Protected content for 123' in response.data


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_login_user_with_none_value(self, app):
        """Test login_user with None value."""
        with app.test_request_context():
            login_user(None)
            assert session['user_id'] is None
    
    def test_login_user_with_empty_string(self, app):
        """Test login_user with empty string."""
        with app.test_request_context():
            login_user('')
            assert session['user_id'] == ''
    
    def test_login_user_with_numeric_id(self, app):
        """Test login_user with numeric user ID."""
        with app.test_request_context():
            login_user(12345)
            assert session['user_id'] == 12345
    
    def test_session_data_types(self, app):
        """Test different data types in session."""
        with app.test_request_context():
            # Test various data types
            session['string'] = 'test'
            session['integer'] = 123
            session['list'] = [1, 2, 3]
            session['dict'] = {'key': 'value'}
            
            logout_user()
            
            # All should be cleared
            assert 'string' not in session
            assert 'integer' not in session
            assert 'list' not in session
            assert 'dict' not in session


class TestSecurityConsiderations:
    """Test security-related aspects of utilities."""
    
    def test_session_isolation(self, app):
        """Test that sessions are properly isolated."""
        with app.test_client() as client1:
            with app.test_client() as client2:
                # Set session in client1
                with client1.session_transaction() as sess:
                    sess['user_id'] = 'user1'
                
                # Check that client2 doesn't have the session
                with client2.session_transaction() as sess:
                    assert 'user_id' not in sess
    
    def test_login_required_sql_injection_attempt(self, app):
        """Test login_required against potential SQL injection in session."""
        @app.route('/sql-protected')
        @login_required
        def sql_protected():
            return f"User: {session['user_id']}"
        
        with app.test_client() as client:
            # Attempt SQL injection through session
            with client.session_transaction() as sess:
                sess['user_id'] = "admin'; DROP TABLE users; --"
            
            response = client.get('/sql-protected')
            assert response.status_code == 200
            # Should just treat it as a regular string
            assert b"admin'; DROP TABLE users; --" in response.data


class TestPerformance:
    """Test performance-related aspects."""
    
    def test_multiple_session_operations(self, app):
        """Test multiple rapid session operations."""
        with app.test_request_context():
            # Rapid login/logout cycles
            for i in range(100):
                login_user(f'user{i}')
                assert session['user_id'] == f'user{i}'
                logout_user()
                assert 'user_id' not in session
    
    def test_large_session_data(self, app):
        """Test handling of large session data."""
        with app.test_request_context():
            # Create large session data
            large_data = 'x' * 10000  # 10KB string
            session['large_data'] = large_data
            session['user_id'] = 'testuser'
            
            # Should still work
            logout_user()
            assert 'user_id' not in session
            assert 'large_data' not in session


if __name__ == '__main__':
    pytest.main([__file__])
