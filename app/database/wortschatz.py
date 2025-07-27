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

class Worschatz(DBInterface):
    """
    Wortschatz database interface class.
    This class provides methods to interact with the wortschatz table in the database.
    Attributes:
        db: The database connection object.
        table_wortschatz (str): The name of the wortschatz table.
    """
    def __init__(self, db):
        super().__init__(db)
        self.table_wortschatz = "DE_EN"

    def get_all(self):
        """
        Retrieves all records from the wortschatz table.
        Returns:
            list: A list of tuples representing all records in the wortschatz table.
        """
        query = f"SELECT * FROM {self.table_wortschatz};"

        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: get_all: {query}")

        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_questions(self, questions, topic):
        """
        Retrieves questions based on the provided parameters.
        Args:
            questions (int): The number of questions to retrieve.
            topic (str): The topic to filter questions by.
        Returns:
            list: A list of tuples representing the questions.
        """
        query = f"SELECT * FROM {self.table_wortschatz} WHERE topic = ? LIMIT ?;"
        
        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: get_questions: {query}, params: ({topic}, {questions})")

        self.cursor.execute(query, (topic, questions))
        return self.cursor.fetchall()
    
    def get_questions_by_keyword(self, questions, keyword):
        """
        Retrieves questions based on keyword search in the keywords column.
        Args:
            questions (int): The number of questions to retrieve.
            keyword (str): The keyword to search for in the keywords column.
        Returns:
            list: A list of tuples representing the questions that match the keyword.
        """
        # Search for keyword in the keywords column using LIKE for partial matching
        query = f"SELECT de, gender, en, keywords FROM {self.table_wortschatz} WHERE keywords LIKE ? ORDER BY RANDOM() LIMIT ?;"
        
        # Add wildcards around the keyword for partial matching
        search_term = f"%{keyword}%"
        
        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: get_questions_by_keyword: {query}, params: ({search_term}, {questions})")

        self.cursor.execute(query, (search_term, questions))
        return self.cursor.fetchall()

    def get_questions_by_keyword_exact(self, questions, keyword):
        """
        Retrieves questions with exact keyword match (for comma-separated keywords).
        Args:
            questions (int): The number of questions to retrieve.
            keyword (str): The exact keyword to search for.
        Returns:
            list: A list of tuples representing the questions with exact keyword match.
        """
        # For exact keyword matching (assuming comma-separated keywords)
        query = f"""SELECT de, gender, en, keywords FROM {self.table_wortschatz} 
                    WHERE keywords = ? 
                    OR keywords LIKE ? 
                    OR keywords LIKE ? 
                    OR keywords LIKE ?
                    ORDER BY RANDOM() LIMIT ?;"""
        
        # Different patterns for exact keyword matching in comma-separated list
        exact_match = keyword
        start_match = f"{keyword},%"
        middle_match = f"%,{keyword},%"
        end_match = f"%,{keyword}"
        
        if DEBUG_MODE:
            print(f"[DEBUG] {FILE_NAME}: get_questions_by_keyword_exact: {query}, params: ({exact_match}, {start_match}, {middle_match}, {end_match}, {questions})")

        self.cursor.execute(query, (exact_match, start_match, middle_match, end_match, questions))
        return self.cursor.fetchall()
    
    def get_random_word(self, questions=10):
        """
        Retrieves a random word from the wortschatz table.
        Returns:
            tuple: A tuple representing a random word from the table.
        """
        query = f"SELECT * FROM {self.table_wortschatz} ORDER BY RANDOM() LIMIT ?;"
        self.cursor.execute(query, (questions,))
        return self.cursor.fetchall()