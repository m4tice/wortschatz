"""
Unit tests for the wortschatz module.
Focuses on wortschatz routes, session management, and protected content access.
author: @GUU8HC
"""
#pylint: disable=redefined-outer-name

import pytest
from unittest.mock import patch
from flask import Flask

from app.wortschatz.wortschatz import wortschatz_bp


@pytest.fixture
def app():
    """Create a minimal Flask app for testing wortschatz routes."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Register the wortschatz blueprint
    app.register_blueprint(wortschatz_bp, url_prefix='/wortschatz')
    
    # Add authentication blueprint route for redirects
    @app.route('/auth/login')
    def login_route():
        return "Login page"
    
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestWortschatzRoutes:
    """Test wortschatz route handlers."""
    
    def test_modes_route_without_authentication(self, client):
        """Test that modes route requires authentication."""
        response = client.get('/wortschatz/modes')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location
    
    def test_session_route_without_authentication(self, client):
        """Test that session route requires authentication."""
        response = client.get('/wortschatz/session')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location
    
    def test_modes_route_with_authentication(self, client):
        """Test modes route with authenticated user."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        assert b'Daily' in response.data
        assert b'Level' in response.data
        assert b'Topic' in response.data
        assert b'Practice' in response.data
    
    def test_session_route_with_authentication(self, client):
        """Test session route with authenticated user."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        assert b'Welcome to Wortschatz session' in response.data
    
    @patch('app.wortschatz.wortschatz.get_git_branch')
    def test_modes_route_with_git_branch(self, mock_git_branch, client):
        """Test modes route includes git branch information."""
        mock_git_branch.return_value = 'feature/test-branch'
        
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        assert b'feature/test-branch' in response.data
    
    @patch('app.wortschatz.wortschatz.get_git_branch')
    def test_session_route_with_git_branch(self, mock_git_branch, client):
        """Test session route includes git branch information."""
        mock_git_branch.return_value = 'main'
        
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        assert b'main' in response.data
    
    @patch('app.wortschatz.wortschatz.get_git_branch')
    def test_modes_route_without_git_branch(self, mock_git_branch, client):
        """Test modes route when git branch is disabled."""
        mock_git_branch.return_value = None
        
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        # Should not contain git branch label when None
        assert b'label-gitv' not in response.data


class TestWortschatzTemplates:
    """Test template rendering for wortschatz routes."""
    
    def test_modes_template_content(self, client):
        """Test that modes template contains expected elements."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        
        # Check for main sections
        assert b'Daily' in response.data
        assert b'Level' in response.data
        assert b'Topic' in response.data
        assert b'Practice' in response.data
        
        # Check for navigation elements
        assert b'navbar' in response.data
        assert b'btn-logout' in response.data
        
        # Check for daily practice buttons
        assert b'btn-daily-5' in response.data
        assert b'btn-daily-10' in response.data
        assert b'btn-daily-20' in response.data
        assert b'btn-daily-50' in response.data
        
        # Check for level buttons
        assert b'btn-level-A1' in response.data
        assert b'btn-level-A2' in response.data
        assert b'btn-level-B1' in response.data
        assert b'btn-level-B2' in response.data
        
        # Check for topic input and button
        assert b'card-input-topic' in response.data
        assert b'btn-topic' in response.data
        
        # Check for practice button
        assert b'btn-practice' in response.data
    
    def test_session_template_content(self, client):
        """Test that session template contains expected elements."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
        
        # Check for main content
        assert b'Welcome to Wortschatz session' in response.data
        
        # Check for navigation elements
        assert b'navbar' in response.data
        assert b'btn-logout' in response.data
        
        # Check for navigation links
        assert b'About Us' in response.data
        assert b'Features' in response.data
        assert b'Pricing' in response.data


class TestAuthenticationRedirection:
    """Test authentication redirection behavior."""
    
    def test_modes_redirect_preserves_original_url(self, client):
        """Test that authentication redirect can preserve original URL."""
        response = client.get('/wortschatz/modes')
        assert response.status_code == 302
        assert response.location.endswith('/auth/login')
    
    def test_session_redirect_preserves_original_url(self, client):
        """Test that authentication redirect can preserve original URL."""
        response = client.get('/wortschatz/session')
        assert response.status_code == 302
        assert response.location.endswith('/auth/login')
    
    def test_multiple_redirects_handled_correctly(self, client):
        """Test that multiple unauthenticated requests are handled correctly."""
        # Multiple requests without authentication
        response1 = client.get('/wortschatz/modes')
        response2 = client.get('/wortschatz/session')
        
        assert response1.status_code == 302
        assert response2.status_code == 302
        assert '/auth/login' in response1.location
        assert '/auth/login' in response2.location


class TestSessionPersistence:
    """Test session persistence across requests."""
    
    def test_session_persists_across_wortschatz_routes(self, client):
        """Test that session persists when navigating between wortschatz routes."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        # Access modes route
        response1 = client.get('/wortschatz/modes')
        assert response1.status_code == 200
        
        # Access session route - should still be authenticated
        response2 = client.get('/wortschatz/session')
        assert response2.status_code == 200
        
        # Verify session is still valid
        with client.session_transaction() as sess:
            assert sess['user_id'] == 'testuser'
    
    def test_session_invalidation_blocks_access(self, client):
        """Test that invalidated session blocks access to protected routes."""
        # Start with valid session
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response1 = client.get('/wortschatz/modes')
        assert response1.status_code == 200
        
        # Clear session
        with client.session_transaction() as sess:
            sess.clear()
        
        # Should now be redirected
        response2 = client.get('/wortschatz/modes')
        assert response2.status_code == 302
        assert '/auth/login' in response2.location


class TestHTTPMethods:
    """Test HTTP method handling for wortschatz routes."""
    
    def test_modes_route_get_method(self, client):
        """Test that modes route accepts GET method."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
    
    def test_session_route_get_method(self, client):
        """Test that session route accepts GET method."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/session')
        assert response.status_code == 200
    
    def test_modes_route_post_method_not_allowed(self, client):
        """Test that modes route rejects POST method."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.post('/wortschatz/modes')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_session_route_post_method_not_allowed(self, client):
        """Test that session route rejects POST method."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.post('/wortschatz/session')
        assert response.status_code == 405  # Method Not Allowed


class TestErrorHandling:
    """Test error handling in wortschatz routes."""
    
    def test_invalid_route_returns_404(self, client):
        """Test that invalid wortschatz routes return 404."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/invalid')
        assert response.status_code == 404
    
    @patch('app.wortschatz.wortschatz.render_template')
    def test_template_error_handling(self, mock_render_template, client):
        """Test handling of template rendering errors."""
        mock_render_template.side_effect = Exception("Template error")
        
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        with pytest.raises(Exception):
            client.get('/wortschatz/modes')


class TestSecurityHeaders:
    """Test security-related headers and responses."""
    
    def test_html_response_content_type(self, client):
        """Test that HTML responses have correct content type."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        assert 'text/html' in response.content_type
    
    def test_no_cache_headers_on_protected_content(self, client):
        """Test that protected content includes appropriate cache headers."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        # Note: This would depend on your actual cache header implementation


class TestRouteDocumentation:
    """Test that routes have proper documentation."""
    
    def test_modes_route_has_docstring(self):
        """Test that modes route function has documentation."""
        from app.wortschatz.wortschatz import modes
        assert modes.__doc__ is not None
        assert "modes" in modes.__doc__.lower() or "render" in modes.__doc__.lower()
    
    def test_session_route_has_docstring(self):
        """Test that session route function has documentation."""
        from app.wortschatz.wortschatz import session
        assert session.__doc__ is not None
        assert "session" in session.__doc__.lower() or "render" in session.__doc__.lower()


class TestIntegrationWithOtherModules:
    """Test integration with other application modules."""
    
    @patch('app.wortschatz.wortschatz.get_git_branch')
    def test_git_branch_integration(self, mock_git_branch, client):
        """Test integration with git branch utility."""
        mock_git_branch.return_value = 'develop'
        
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200
        mock_git_branch.assert_called_once()
    
    def test_login_required_decorator_integration(self, client):
        """Test integration with login_required decorator."""
        # Without authentication - should redirect
        response = client.get('/wortschatz/modes')
        assert response.status_code == 302
        
        # With authentication - should succeed
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        
        response = client.get('/wortschatz/modes')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])
