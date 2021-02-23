from typing import Union

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.results import UpdateResult

from mongo import interface


class BaseClass(object):
    """
    Base MongoDB DB Class. Provides basic method and properties that all other DB Classes will need.
    If not username or password is provided - authenticate without username and password.
    """
    def __init__(
            self,
            ip: str = "127.0.0.1",
            username: str = None,
            password: str = None):
        """
        Constructor method.
        :param ip: ip of instance to connect to
        :param username: username to login to instance with
        :param password: password to login to instance with
        """
        self.cli = interface.get_client(ip, username, password)
        self._vault = None

    @property
    def mongo_client(self) -> MongoClient:
        """
        Pymongo Client Object
        :return: MongoClient object
        """
        return self.cli

    @property
    def vault(self) -> Collection:
        """
        vault property
        :return: Collection object
        """
        return self._vault

    def insert(self, document: Union[dict, list]) -> list:
        """
        Inserts the given object into this class' Collection object.
        :param document: document(s) to insert as dict or list of dicts
        :return: list of inserted IDs
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        if not isinstance(document, (list, dict)):
            raise IncorrectDocument("Given document isn't a dictionary or a list.")
        elif isinstance(document, list) and not all([isinstance(k, dict) for k in document]):
            raise IncorrectDocument("Not all documents in the list are dictionaries.")
        rets = interface.insert(self._vault, document)
        return rets

    def update(self, parameters: dict, updated_vals: dict) -> UpdateResult:
        """
        Updates all documents based on the given parameters with the provided values.
        :param parameters:
        :param updated_vals:
        :return: UpdateResult object
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        rets = interface.update(self.vault, parameters, updated_vals)
        return rets

    def delete(self, parameters: dict, many: bool = True) -> int:
        """
        Deletes documents based on the given parameters. If many=False, only deletes one else it deletes all matches.
        :param many: whether to delete all matching documents or just one
        :param parameters: Parameters to match and delete on. Must be a dictionary.
        :return: number of deleted
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        rets = interface.delete(self.vault, parameters, many)
        return rets

    def query(
            self,
            parameters: dict,
            limit: int = 1000,
            projection: dict = None,
            as_gen: bool = False) -> Union[list, Cursor]:
        """
        Searches a collection for documents based on given parameters.
        Parameters should be dictionaries : {key : search}. Where key is an existing key in the collection and
        search is either a value or an expression.
        Expressions can either be {operator: value} or {"$regex": regex_expression}. Regex can only be used on string fields.
        Valid operators: https://docs.mongodb.com/manual/reference/operator/query-comparison/
        Parameter examples:
            parameters = {"test_name": "tst_englishUK"}
            parameters = {"test_name": {"$gt": "tst_S"}}
            parameters = {"test_name": {"$regex": "tst_g.*"}}
        Projection examples:
            projection = {"_id": False}
        Args:
            parameters : dictionary as above
            limit : max number of results to return
            projection : dict of keys to return for each result
            as_gen : True returns generator (mongoDB cursor obj) and false returns list of results
        Returns a generator (cursor obj) if as_gen else returns a list of results
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        return interface.query(self.vault, parameters, limit, projection, as_gen)

    def get_collection_names(self) -> Union[None, list]:
        """
        Gets collection names of database
        :return:
        """
        if not hasattr(self, "database"):
            raise NoVaultError("No vault instantiated.")
        return interface.get_collection_names(self.database)

    def create_index(self, field: str) -> Union[bool, str, list]:
        """
        Creates an index on the current collection
        :param field: str of field name to index of
        :return:
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        return interface.create_index(self.vault, field)

    def get_indexes(self) -> list:
        """
        Gets a list of indexes on the current collection
        :return:
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        return interface.get_indexes(self.vault)


class NoVaultError(Exception):
    """
    Custom exception for when we haven't instantiated a vault properly
    """
    def __init__(self, message):
        super(NoVaultError, self).__init__(message)


class IncorrectDocument(Exception):
    """
        Custom exception for when we haven't got a document formatted correctly
        """
    def __init__(self, message):
        super(IncorrectDocument, self).__init__(message)
