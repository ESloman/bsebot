"""Generic collection interface."""

from pymongo.results import UpdateResult

from mongo import interface
from mongo.db_classes import BestSummerEverPointsDB


class DataStore(BestSummerEverPointsDB):
    """Class for interacting with the 'generic_datastore' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method for the class. Initialises the collection object."""
        super().__init__()
        self._vault = interface.get_collection(self.database, "generic_datastore")

    def get_starting_words(self) -> dict | None:
        """Gets starting wordle words.

        Returns:
            dict | None: _description_
        """
        ret = self.query({"type": "wordle_starting_words"})
        if not ret:
            return None
        return ret[0]

    def set_starting_words(self, words: list[str]) -> UpdateResult:
        """Sets starting wordle words.

        Args:
            words (list[str]): _description_

        Returns:
            UpdateResult: _description_
        """
        return self.update({"type": "wordle_starting_words"}, {"$set": {"words": words}})

    def add_starting_word(self, word: str) -> UpdateResult:
        """Adds a new starting word to the datastore.

        Args:
            word (str): the word to add

        Returns:
            UpdateResult: the update result
        """
        return self.update({"type": "wordle_starting_words"}, {"$push": {"words": word}})
