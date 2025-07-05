"""
author: @GUU8HC
"""
# pylint: disable=wrong-import-position
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught

from app.settings import DEBUG_MODE

from .db_interface import DBInterface

if DEBUG_MODE:
    FILE_NAME = "user.py"

class User(DBInterface):
    """
    User database interface class.
    This class provides methods to interact with the user table in the database.
    Attributes:
        db: The database connection object.
        table_user (str): The name of the user table.
        Get all users from the user table.
        Returns:
            list: A list of tuples, each representing a user record.
        pass
        Get a user by their username.
        Args:
            username (str): The username of the user to retrieve.
        Returns:
            tuple: A tuple representing the user record, or None if no user is found.
        pass
    """
    def __init__(self, db):
        super().__init__(db)
        self.table_user = "user"

    def get_all(self):
        """
        Retrieves all records from the user table.
        Executes a SQL query to fetch all records from the user table and returns the result.
        Returns:
            list: A list of tuples representing all records in the user table.        
        """
        query = f"SELECT * FROM {self.table_user};"

        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: get_all: {query}")

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_user_by_username(self, username):
        """
        Retrieves a user record from the database by username.
        Args:
            username (str): The username of the user to retrieve.
        Returns:
            dict: A dictionary containing the user record if found, otherwise None.
        Raises:
            Exception: If there is an error executing the database query.
        """
        # Old implementation with risk when 'username' is [ admin' OR '1'='1 ]
        # query = f"SELECT * FROM {self.table_user} WHERE username = '{username}';"

        # if DEBUG_MODE:
        #     print(f"[DEBUG] {FILE_NAME}: get_user_by_username: {query} with username: {username}")

        # self.cursor.execute(query)
        # result = self.cursor.fetchone()

        # New implementation with SQL injection protection
        query = f"SELECT * FROM {self.table_user} WHERE username = ?;"

        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: get_user_by_username: {query} with username: {username}")

        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()

        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: query_result: {result}")

        return result

    def create_user(self, username, password):
        """
        Creates a new user record in the database.
        Args:
            username (str): The username of the new user.
            password (str): The password of the new user.
        Returns:
            bool: True if the user was created successfully, False otherwise.
        Raises:
            Exception: If there is an error executing the database query.
        """
        query = f"INSERT INTO {self.table_user} (userid, username, password) VALUES (?, ?, ?);"

        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: create_user: {query} with username: {username} and password: {password}")

        try:
            self.cursor.execute(query, (username, username, password))
            self.connection.commit()
            return True

        except Exception as e:
            print(f"[ERROR] {FILE_NAME}: create_user: {e}")
            return False

    def remove_user(self, username):
        """
        Removes a user record from the database by username.
        Args:
            username (str): The username of the user to remove.
        Returns:
            bool: True if the user was removed successfully, False otherwise.
        Raises:
            Exception: If there is an error executing the database query.
        """
        query = f"DELETE FROM {self.table_user} WHERE userid = ?;"

        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: remove_user: {query} with username: {username}")

        try:
            self.cursor.execute(query, (username,))
            self.connection.commit()
            return True

        except Exception as e:
            print(f"[ERROR] {FILE_NAME}: remove_user: {e}")
            return False

    def remove_invalid_user(self):
        """
        Removes invalid user records from the database.
        This method is a placeholder for future implementation.
        """
        query = f"DELETE FROM {self.table_user} WHERE userid IS NULL OR trim(userid) = '';"

        try:
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"[ERROR] {FILE_NAME}: remove_invalid_user: {e}")
            return False

    def remove_all(self):
        """
        Removes all user records from the database.
        This method is a placeholder for future implementation.
        """
        query = f"DELETE FROM {self.table_user};"

        try:
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"[ERROR] {FILE_NAME}: remove_all: {e}")
            return False
