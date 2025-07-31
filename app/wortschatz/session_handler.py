"""
author: @guu8hc
"""

import unicodedata
import re

from app.database import deen_db

class SessionHandler:
    """
    Session handler for managing the session state in the Wortschatz application.
    """

    def __init__(self):
        """
        Constructor
        """
        self.db = deen_db
        self.questions = []

    def set_session(self, questions=10, topic=None):
        if topic == "random" or topic is None:
            # Use random words when topic is "random" or None
            data = self.db.get_random_word(questions=questions)
        else:
            # Use keyword search for specific topics
            data = self.db.get_questions_by_keyword(questions=questions, keyword=topic)
        self.questions = self.__transform(data)
        print(f"[DEBUG] Loaded questions: {list(self.questions.keys())}")
        print(f"[DEBUG] Question data: {self.questions}")

    def __transform(self, data):
        """
        Transform the data into a list of questions.
        e.g.:
            car : {"de" : "Auto", "gender" : "neutral", "keys" : "vehicle"}
        """
        transformed = {
            word[2] : {
                "de": word[0],
                "gender": word[1],
                "keys": word[3]
            }
            for word in data
        }
        return transformed
    
    def __get_definiter_artikel(self, gender):
        """
        Get the correct article for a given gender.
        """
        if gender == "male" or gender == "masculine":
            return "der"
        elif gender == "female" or gender == "feminine":
            return "die"
        else:
            return "das"
        
    def __normalize_german(self, word: str) -> bool:
        """
        validate("Mädchen straße", "Maedchenstraße")  # True
        validate("Gute nacht", "gute Nacht")          # True
        validate("schloss", "Schloß")                 # True
        validate("gross", "groß")                     # True
        validate("Apfel", "Apfel")                    # True
        validate(" Apfel ", "Apfel")                  # True
        validate("gutemorgen", "Gute Morgen")         # False (if spacing matters)
        """
        translit = {
            "ä": "ae", "ö": "oe", "ü": "ue",
            "Ä": "ae", "Ö": "oe", "Ü": "ue",
            "ß": "ss"
        }
        word = word.lower()
        word = unicodedata.normalize('NFKD', word)
        word = ''.join(translit.get(c, c) for c in word)
        word = re.sub(r'\s+', ' ', word.strip())  # collapse multiple spaces
        return word

    def get_questions(self) -> list:
        """
        Get questions for the session.
        """
        return list(self.questions.keys())
    
    def validate(self, question: str, answer: str) -> bool:
        """
        Validate user input against actual answers.
        """
        
        # get definite article
        artikel = self.__get_definiter_artikel(self.questions[question.capitalize()]['gender'])

        # get translation from data base
        translation = self.questions[question.capitalize()]['de']

        # join article and translation
        expectation = f"{artikel} {translation}"

        # normalize both expectation and answer
        expectation = self.__normalize_german(expectation)
        answer = self.__normalize_german(answer)

        print(f"[DEBUG] Validating: {question} -> {answer} against {expectation}")
        return answer == expectation
