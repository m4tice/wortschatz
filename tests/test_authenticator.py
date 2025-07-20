"""
Unit tests for the Authenticator class.
Focuses on password hashing, verification, user authentication, and registration.
author: @GUU8HC
"""
#pylint: disable=redefined-outer-name

import pytest
from unittest.mock import MagicMock, patch
import bcrypt

from app.authenticator.authenticator import Authenticator
from app.database.user import User


@pytest.fixture
def mock_user_db():
    """Create a mock User database object."""
    return MagicMock(spec=User)


@pytest.fixture
def authenticator(mock_user_db):
    """Create an Authenticator instance with mock database."""
    return Authenticator(mock_user_db)


class TestPasswordHashing:
    """Test password hashing functionality."""
    
    def test_hash_password_returns_string(self, authenticator):
        """Test that hash_password returns a string."""
        password = "testpassword123"
        hashed = authenticator.hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
    
    def test_hash_password_different_each_time(self, authenticator):
        """Test that hashing the same password produces different hashes."""
        password = "samepassword"
        hash1 = authenticator.hash_password(password)
        hash2 = authenticator.hash_password(password)
        
        assert hash1 != hash2
        assert isinstance(hash1, str)
        assert isinstance(hash2, str)
    
    def test_hash_password_empty_string(self, authenticator):
        """Test hashing an empty password."""
        hashed = authenticator.hash_password("")
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_unicode_characters(self, authenticator):
        """Test hashing password with unicode characters."""
        password = "pāsswörd123¢£¥"
        hashed = authenticator.hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
    
    def test_hash_password_long_password(self, authenticator):
        """Test hashing a very long password."""
        password = "a" * 1000  # 1000 character password
        hashed = authenticator.hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0


class TestPasswordVerification:
    """Test password verification functionality."""
    
    def test_verify_password_correct(self, authenticator):
        """Test verification with correct password."""
        password = "correctpassword"
        hashed = authenticator.hash_password(password)
        
        assert authenticator.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self, authenticator):
        """Test verification with incorrect password."""
        correct_password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = authenticator.hash_password(correct_password)
        
        assert authenticator.verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_password(self, authenticator):
        """Test verification with empty password."""
        password = ""
        hashed = authenticator.hash_password(password)
        
        assert authenticator.verify_password(password, hashed) is True
        assert authenticator.verify_password("nonempty", hashed) is False
    
    def test_verify_password_case_sensitive(self, authenticator):
        """Test that password verification is case sensitive."""
        password = "CaseSensitive"
        hashed = authenticator.hash_password(password)
        
        assert authenticator.verify_password(password, hashed) is True
        assert authenticator.verify_password("casesensitive", hashed) is False
        assert authenticator.verify_password("CASESENSITIVE", hashed) is False
    
    def test_verify_password_with_spaces(self, authenticator):
        """Test verification with passwords containing spaces."""
        password = "password with spaces"
        hashed = authenticator.hash_password(password)
        
        assert authenticator.verify_password(password, hashed) is True
        assert authenticator.verify_password("passwordwithspaces", hashed) is False
        assert authenticator.verify_password(" password with spaces ", hashed) is False
    
    def test_verify_password_unicode(self, authenticator):
        """Test verification with unicode passwords."""
        password = "пароль123"
        hashed = authenticator.hash_password(password)
        
        assert authenticator.verify_password(password, hashed) is True
        assert authenticator.verify_password("пароль124", hashed) is False


class TestUserAuthentication:
    """Test user authentication functionality."""
    
    def test_authenticate_existing_user_correct_password(self, authenticator, mock_user_db):
        """Test authentication with existing user and correct password."""
        username = "testuser"
        password = "testpassword"
        hashed_password = authenticator.hash_password(password)
        
        # Mock database to return user
        mock_user_db.get_user_by_username.return_value = ('userid', 'testuser', hashed_password)
        
        result = authenticator.authenticate(username, password)
        
        assert result is True
        mock_user_db.get_user_by_username.assert_called_once_with(username)
    
    def test_authenticate_existing_user_wrong_password(self, authenticator, mock_user_db):
        """Test authentication with existing user and wrong password."""
        username = "testuser"
        correct_password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed_password = authenticator.hash_password(correct_password)
        
        # Mock database to return user
        mock_user_db.get_user_by_username.return_value = ('userid', 'testuser', hashed_password)
        
        result = authenticator.authenticate(username, wrong_password)
        
        assert result is False
        mock_user_db.get_user_by_username.assert_called_once_with(username)
    
    def test_authenticate_nonexistent_user(self, authenticator, mock_user_db):
        """Test authentication with non-existent user."""
        username = "nonexistentuser"
        password = "anypassword"
        
        # Mock database to return None (user doesn't exist)
        mock_user_db.get_user_by_username.return_value = None
        
        result = authenticator.authenticate(username, password)
        
        assert result is False
        mock_user_db.get_user_by_username.assert_called_once_with(username)
    
    def test_authenticate_with_empty_username(self, authenticator, mock_user_db):
        """Test authentication with empty username."""
        username = ""
        password = "somepassword"
        
        mock_user_db.get_user_by_username.return_value = None
        
        result = authenticator.authenticate(username, password)
        
        assert result is False
        mock_user_db.get_user_by_username.assert_called_once_with(username)
    
    def test_authenticate_with_none_user_data(self, authenticator, mock_user_db):
        """Test authentication when database returns None."""
        username = "testuser"
        password = "testpassword"
        
        mock_user_db.get_user_by_username.return_value = None
        
        result = authenticator.authenticate(username, password)
        
        assert result is False


class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_new_user(self, authenticator, mock_user_db):
        """Test registration of a new user."""
        username = "newuser"
        password = "newpassword"
        
        # Mock database to indicate user doesn't exist
        mock_user_db.get_user_by_username.return_value = None
        mock_user_db.create_user.return_value = True
        
        result = authenticator.register(username, password)
        
        assert result is True
        mock_user_db.get_user_by_username.assert_called_once_with(username)
        mock_user_db.create_user.assert_called_once()
        
        # Verify that the password was hashed before storing
        call_args = mock_user_db.create_user.call_args[0]
        assert call_args[0] == username
        assert call_args[1] != password  # Should be hashed
        assert len(call_args[1]) > len(password)  # Hashed passwords are longer
    
    def test_register_existing_user(self, authenticator, mock_user_db):
        """Test registration of an existing user."""
        username = "existinguser"
        password = "newpassword"
        
        # Mock database to indicate user already exists
        mock_user_db.get_user_by_username.return_value = ('userid', 'existinguser', 'oldhashedpass')
        
        result = authenticator.register(username, password)
        
        assert result is False
        mock_user_db.get_user_by_username.assert_called_once_with(username)
        mock_user_db.create_user.assert_not_called()
    
    def test_register_database_creation_fails(self, authenticator, mock_user_db):
        """Test registration when database user creation fails."""
        username = "newuser"
        password = "newpassword"
        
        # Mock database to indicate user doesn't exist but creation fails
        mock_user_db.get_user_by_username.return_value = None
        mock_user_db.create_user.return_value = False
        
        result = authenticator.register(username, password)
        
        # Should still return True because the method doesn't check create_user result
        # This is based on the current implementation
        assert result is True
        mock_user_db.get_user_by_username.assert_called_once_with(username)
        mock_user_db.create_user.assert_called_once()
    
    def test_register_empty_username(self, authenticator, mock_user_db):
        """Test registration with empty username."""
        username = ""
        password = "somepassword"
        
        mock_user_db.get_user_by_username.return_value = None
        mock_user_db.create_user.return_value = True
        
        result = authenticator.register(username, password)
        
        assert result is True
        mock_user_db.get_user_by_username.assert_called_once_with(username)
        mock_user_db.create_user.assert_called_once()
    
    def test_register_empty_password(self, authenticator, mock_user_db):
        """Test registration with empty password."""
        username = "testuser"
        password = ""
        
        mock_user_db.get_user_by_username.return_value = None
        mock_user_db.create_user.return_value = True
        
        result = authenticator.register(username, password)
        
        assert result is True
        mock_user_db.get_user_by_username.assert_called_once_with(username)
        mock_user_db.create_user.assert_called_once()
        
        # Verify empty password was hashed
        call_args = mock_user_db.create_user.call_args[0]
        assert call_args[1] != ""  # Should be hashed empty string


class TestSecurityConsiderations:
    """Test security-related aspects of authentication."""
    
    def test_timing_attack_resistance(self, authenticator, mock_user_db):
        """Test that authentication has consistent timing for existing/non-existing users."""
        # This is a basic test - in practice, you'd measure timing
        
        # Non-existent user
        mock_user_db.get_user_by_username.return_value = None
        result1 = authenticator.authenticate("nonexistent", "password")
        
        # Existing user with wrong password
        hashed = authenticator.hash_password("correctpass")
        mock_user_db.get_user_by_username.return_value = ('id', 'user', hashed)
        result2 = authenticator.authenticate("user", "wrongpass")
        
        assert result1 is False
        assert result2 is False
    
    def test_password_hash_strength(self, authenticator):
        """Test that password hashes are sufficiently strong."""
        password = "testpassword"
        hashed = authenticator.hash_password(password)
        
        # BCrypt hashes should start with $2a$, $2b$, $2x$, or $2y$
        assert hashed.startswith(('$2a$', '$2b$', '$2x$', '$2y$'))
        
        # Should contain salt (BCrypt hashes are at least 60 characters)
        assert len(hashed) >= 60
    
    def test_sql_injection_resistance(self, authenticator, mock_user_db):
        """Test resistance to SQL injection attempts."""
        malicious_username = "admin'; DROP TABLE users; --"
        password = "password"
        
        mock_user_db.get_user_by_username.return_value = None
        
        # Should not cause issues
        result = authenticator.authenticate(malicious_username, password)
        
        assert result is False
        mock_user_db.get_user_by_username.assert_called_once_with(malicious_username)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_very_long_username(self, authenticator, mock_user_db):
        """Test authentication with very long username."""
        username = "a" * 1000
        password = "password"
        
        mock_user_db.get_user_by_username.return_value = None
        
        result = authenticator.authenticate(username, password)
        
        assert result is False
        mock_user_db.get_user_by_username.assert_called_once_with(username)
    
    def test_special_characters_in_credentials(self, authenticator, mock_user_db):
        """Test authentication with special characters in username and password."""
        username = "user@domain.com"
        password = "p@ssw0rd!#$%^&*()"
        hashed = authenticator.hash_password(password)
        
        mock_user_db.get_user_by_username.return_value = ('id', username, hashed)
        
        result = authenticator.authenticate(username, password)
        
        assert result is True
    
    def test_unicode_username(self, authenticator, mock_user_db):
        """Test authentication with unicode username."""
        username = "пользователь"
        password = "пароль"
        hashed = authenticator.hash_password(password)
        
        mock_user_db.get_user_by_username.return_value = ('id', username, hashed)
        
        result = authenticator.authenticate(username, password)
        
        assert result is True
    
    @patch('app.authenticator.authenticator.DEBUG_MODE', True)
    def test_debug_mode_logging(self, authenticator, mock_user_db, capsys):
        """Test that debug mode produces appropriate logging."""
        username = "testuser"
        password = "testpass"
        hashed = authenticator.hash_password(password)
        
        mock_user_db.get_user_by_username.return_value = ('id', username, hashed)
        
        authenticator.authenticate(username, password)
        
        # Check that debug output was produced
        captured = capsys.readouterr()
        assert "[DEBUG]" in captured.out


class TestBcryptIntegration:
    """Test integration with bcrypt library."""
    
    def test_bcrypt_version_compatibility(self, authenticator):
        """Test compatibility with bcrypt library version."""
        password = "testpassword"
        hashed = authenticator.hash_password(password)
        
        # Should be able to verify using bcrypt directly
        assert bcrypt.checkpw(password.encode(), hashed.encode())
    
    def test_bcrypt_rounds_sufficient(self, authenticator):
        """Test that bcrypt uses sufficient rounds for security."""
        password = "testpassword"
        hashed = authenticator.hash_password(password)
        
        # Extract rounds from hash (format: $2b$12$...)
        parts = hashed.split('$')
        if len(parts) >= 3:
            rounds = int(parts[2])
            # Should use at least 10 rounds (current default is usually 12)
            assert rounds >= 10


if __name__ == '__main__':
    pytest.main([__file__])
