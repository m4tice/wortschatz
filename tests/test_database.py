"""
Unit tests for database operations.
Focuses on User model, database interface, and data persistence.
author: @GUU8HC
"""
#pylint: disable=redefined-outer-name

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch, MagicMock, call

from app.database.user import User
from app.database.db_interface import DBInterface


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing."""
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
def mock_db():
    """Create mock database objects."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    return mock_connection, mock_cursor


class TestDBInterface:
    """Test database interface base class."""
    
    @patch('app.database.db_interface.sqlite3')
    def test_db_interface_init_success(self, mock_sqlite):
        """Test successful database interface initialization."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        db_interface = DBInterface('test.db')
        
        assert db_interface.db == 'test.db'
        assert db_interface.connection == mock_connection
        assert db_interface.cursor == mock_cursor
        mock_sqlite.connect.assert_called_once_with('test.db', check_same_thread=False)
    
    def test_db_interface_init_none_db(self):
        """Test database interface initialization with None database."""
        db_interface = DBInterface(None)
        
        assert db_interface.db is None
        assert db_interface.connection is None
        assert db_interface.cursor is None


class TestUserModel:
    """Test User model database operations."""
    
    def test_user_init(self, temp_db):
        """Test User model initialization."""
        user = User(temp_db)
        assert user.table_user == "user"
        assert user.db == temp_db
        assert user.connection is not None
        assert user.cursor is not None
    
    def test_get_all_users_empty(self, temp_db):
        """Test getting all users from empty database."""
        user = User(temp_db)
        users = user.get_all()
        assert users == []
    
    def test_get_all_users_with_data(self, temp_db):
        """Test getting all users with data in database."""
        # Insert test data
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user VALUES (?, ?, ?)", ('user1', 'user1', 'pass1'))
        cursor.execute("INSERT INTO user VALUES (?, ?, ?)", ('user2', 'user2', 'pass2'))
        conn.commit()
        conn.close()
        
        user = User(temp_db)
        users = user.get_all()
        
        assert len(users) == 2
        assert ('user1', 'user1', 'pass1') in users
        assert ('user2', 'user2', 'pass2') in users
    
    def test_get_user_by_username_exists(self, temp_db):
        """Test getting existing user by username."""
        # Insert test data
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user VALUES (?, ?, ?)", ('testuser', 'testuser', 'hashedpass'))
        conn.commit()
        conn.close()
        
        user = User(temp_db)
        result = user.get_user_by_username('testuser')
        
        assert result is not None
        assert result[0] == 'testuser'
        assert result[1] == 'testuser'
        assert result[2] == 'hashedpass'
    
    def test_get_user_by_username_not_exists(self, temp_db):
        """Test getting non-existing user by username."""
        user = User(temp_db)
        result = user.get_user_by_username('nonexistent')
        assert result is None
    
    def test_create_user_success(self, temp_db):
        """Test successful user creation."""
        user = User(temp_db)
        result = user.create_user('newuser', 'hashedpass')
        
        assert result is True
        
        # Verify user was created
        created_user = user.get_user_by_username('newuser')
        assert created_user is not None
        assert created_user[0] == 'newuser'
        assert created_user[1] == 'newuser'
        assert created_user[2] == 'hashedpass'
    
    def test_create_user_duplicate(self, temp_db):
        """Test creating user with duplicate username."""
        user = User(temp_db)
        
        # Create first user
        result1 = user.create_user('testuser', 'pass1')
        assert result1 is True
        
        # Try to create duplicate user
        result2 = user.create_user('testuser', 'pass2')
        assert result2 is False
    
    def test_remove_user_success(self, temp_db):
        """Test successful user removal."""
        # Create user first
        user = User(temp_db)
        user.create_user('testuser', 'hashedpass')
        
        # Verify user exists
        assert user.get_user_by_username('testuser') is not None
        
        # Remove user
        result = user.remove_user('testuser')
        assert result is True
        
        # Verify user was removed
        assert user.get_user_by_username('testuser') is None
    
    def test_remove_user_not_exists(self, temp_db):
        """Test removing non-existing user."""
        user = User(temp_db)
        result = user.remove_user('nonexistent')
        assert result is True  # SQL DELETE doesn't fail for non-existing records
    
    def test_remove_invalid_user(self, temp_db):
        """Test removing invalid users."""
        # Insert valid and invalid users
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user VALUES (?, ?, ?)", ('validuser', 'validuser', 'pass'))
        cursor.execute("INSERT INTO user VALUES (?, ?, ?)", (None, 'invaliduser1', 'pass'))
        cursor.execute("INSERT INTO user VALUES (?, ?, ?)", ('', 'invaliduser2', 'pass'))
        cursor.execute("INSERT INTO user VALUES (?, ?, ?)", ('   ', 'invaliduser3', 'pass'))
        conn.commit()
        conn.close()
        
        user = User(temp_db)
        
        # Check initial count
        all_users = user.get_all()
        assert len(all_users) == 4
        
        # Remove invalid users
        result = user.remove_invalid_user()
        assert result is True
        
        # Check that only valid user remains
        remaining_users = user.get_all()
        assert len(remaining_users) == 1
        assert remaining_users[0][0] == 'validuser'
    
    def test_remove_all_users(self, temp_db):
        """Test removing all users."""
        # Create multiple users
        user = User(temp_db)
        user.create_user('user1', 'pass1')
        user.create_user('user2', 'pass2')
        user.create_user('user3', 'pass3')
        
        # Verify users exist
        all_users = user.get_all()
        assert len(all_users) == 3
        
        # Remove all users
        result = user.remove_all()
        assert result is True
        
        # Verify all users were removed
        remaining_users = user.get_all()
        assert len(remaining_users) == 0


class TestUserModelWithMocks:
    """Test User model with mocked database operations."""
    
    @patch('app.database.user.sqlite3')
    def test_get_all_with_mock(self, mock_sqlite):
        """Test get_all method with mocked database."""
        mock_connection, mock_cursor = mock_db()
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('user1', 'user1', 'pass1')]
        
        user = User('test.db')
        result = user.get_all()
        
        mock_cursor.execute.assert_called_once_with("SELECT * FROM user;")
        mock_cursor.fetchall.assert_called_once()
        assert result == [('user1', 'user1', 'pass1')]
    
    @patch('app.database.user.sqlite3')
    def test_create_user_with_mock(self, mock_sqlite):
        """Test create_user method with mocked database."""
        mock_connection, mock_cursor = mock_db()
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        user = User('test.db')
        result = user.create_user('testuser', 'hashedpass')
        
        expected_query = "INSERT INTO user (userid, username, password) VALUES (?, ?, ?);"
        mock_cursor.execute.assert_called_once_with(
            expected_query, ('testuser', 'testuser', 'hashedpass')
        )
        mock_connection.commit.assert_called_once()
        assert result is True
    
    @patch('app.database.user.sqlite3')
    def test_create_user_exception_with_mock(self, mock_sqlite):
        """Test create_user method exception handling with mocked database."""
        mock_connection, mock_cursor = mock_db()
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        user = User('test.db')
        result = user.create_user('testuser', 'hashedpass')
        
        assert result is False
    
    @patch('app.database.user.sqlite3')
    def test_remove_user_with_mock(self, mock_sqlite):
        """Test remove_user method with mocked database."""
        mock_connection, mock_cursor = mock_db()
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        user = User('test.db')
        result = user.remove_user('testuser')
        
        expected_query = "DELETE FROM user WHERE userid = ?;"
        mock_cursor.execute.assert_called_once_with(expected_query, ('testuser',))
        mock_connection.commit.assert_called_once()
        assert result is True


class TestSQLInjectionPrevention:
    """Test SQL injection prevention measures."""
    
    def test_get_user_by_username_parameterized(self, temp_db):
        """Test that get_user_by_username uses parameterized queries."""
        user = User(temp_db)
        
        # Try SQL injection attempt
        malicious_username = "admin' OR '1'='1"
        result = user.get_user_by_username(malicious_username)
        
        # Should return None because the exact string doesn't exist
        assert result is None
    
    def test_create_user_parameterized(self, temp_db):
        """Test that create_user uses parameterized queries."""
        user = User(temp_db)
        
        # Try SQL injection attempt in username
        malicious_username = "admin'; DROP TABLE user; --"
        result = user.create_user(malicious_username, 'password')
        
        # Should succeed without affecting the database structure
        assert result is True
        
        # Verify table still exists by getting all users
        users = user.get_all()
        assert isinstance(users, list)


class TestDatabaseErrorHandling:
    """Test database error handling scenarios."""
    
    @patch('app.database.user.sqlite3')
    def test_connection_error_handling(self, mock_sqlite):
        """Test handling of database connection errors."""
        mock_sqlite.connect.side_effect = sqlite3.Error("Connection failed")
        
        # Should not raise exception
        with pytest.raises(sqlite3.Error):
            User('invalid.db')
    
    @patch('app.database.user.sqlite3')
    def test_query_error_handling(self, mock_sqlite):
        """Test handling of database query errors."""
        mock_connection, mock_cursor = mock_db()
        mock_sqlite.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Query failed")
        
        user = User('test.db')
        
        # Methods should handle exceptions gracefully
        assert user.create_user('test', 'pass') is False
        assert user.remove_user('test') is False
        assert user.remove_invalid_user() is False
        assert user.remove_all() is False


if __name__ == '__main__':
    pytest.main([__file__])
