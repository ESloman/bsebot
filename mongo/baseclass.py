"""Mongo baseclass."""

import os

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import UpdateResult

from mongo import interface


class BaseClass:
    """Base MongoDB DB Class.

    Provides basic method and properties that all other DB Classes will need.
    If not username or password is provided - authenticate without username and password.
    """

    _NO_VAULT_MESSAGE = "No vault instantiated."
    _MINIMUM_PROJECTION_DICT: dict | None = None

    def __init__(
        self,
        ip: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str = "bestsummereverpoints",
        collection: str | None = None,
    ) -> None:
        """Initialisation method.

        Args:
            ip (str, optional): ip to connect to. Defaults to "127.0.0.1".
            username (str | None, optional): username. Defaults to None.
            password (str | None, optional): password. Defaults to None.
            database (str): the database to connect to. Defaults to 'bestsummereverpoints'.
            collection (str | None): the collection to connect to. Defaults to None.
        """
        if ip is None:
            ip = os.environ.get("MONGODB_IP", "127.0.0.1")
        self.cli = interface.get_client(ip, username, password)
        self._bse_db = interface.get_database(self.mongo_client, database)
        self._vault = interface.get_collection(self.database, collection) if collection else None

    @property
    def database(self) -> Database:
        """Basic database property.

        Returns:
            Database: the database
        """
        return self._bse_db

    @property
    def mongo_client(self) -> MongoClient:
        """Mongo client property.

        Returns:
            MongoClient: the client
        """
        return self.cli

    @property
    def vault(self) -> Collection:
        """Vault property.

        Raises:
            NoVaultError: raised when vault isn't instantiated

        Returns:
            Collection: the collection/vault
        """
        if self._vault is None:
            msg = self._NO_VAULT_MESSAGE
            raise NoVaultError(msg)
        return self._vault

    @property
    def minimum_projection(self) -> dict | None:
        """Minimum projection property.

        Returns:
            dict | None: None, or the minimum projection
        """
        return self._MINIMUM_PROJECTION_DICT

    def _update_projection(self, projection: dict[str, any]) -> None:
        """Updates the given projection with the minimum values defined.

        Args:
            projection (dict): _description_
        """
        if not self.minimum_projection:
            return

        if all(value is False for value in projection.values()):
            # everything is false - make sure we're not excluding things we care about
            for key in self.minimum_projection:
                if key in projection:
                    projection.pop(key)
            return

        projection.update(self.minimum_projection)

    @staticmethod
    def make_data_class(data: dict[str, any]) -> any:
        """Method to convert query data into a dataclass.

        Expected to be implemented by each collection class.

        Args:
            data (dict[str, any]): the data to convert

        Raises:
            NotImplementedError: raised when not implemented

        Returns:
            any: the dataclass type
        """
        raise NotImplementedError

    def insert(self, document: dict | list) -> list[ObjectId]:
        """Inserts the given object into this class' Collection object.

        Args:
            document (dict | list): the document or list of documents to insert

        Raises:
            IncorrectDocument: raised when document isn't formatted correctly

        Returns:
            list[ObjectId]: list of inserted IDs
        """
        if not isinstance(document, list | dict):
            msg = "Given document isn't a dictionary or a list."
            raise IncorrectDocumentError(msg)

        if isinstance(document, list) and not all(isinstance(k, dict) for k in document):
            msg = "Not all documents in the list are dictionaries."
            raise IncorrectDocumentError(msg)

        return interface.insert(self.vault, document)

    def update(self, parameters: dict[str, any], updated_vals: dict[str, any], many: bool = False) -> UpdateResult:
        """Updates all documents based on the given parameters with the provided values.

        Args:
            parameters (dict): the parameters to match documents on
            updated_vals (dict): the update parameters
            many (bool, optional): whether to update many. Defaults to False.

        Returns:
            UpdateResult: the update result
        """
        return interface.update(self.vault, parameters, updated_vals, many)

    def delete(self, parameters: dict[str, any], many: bool = True) -> int:
        """Deletes documents based on the given parameters.

        If many=False, only deletes one else it deletes all matches.

        Args:
            parameters (dict): the parameters to match documents on
            many (bool, optional): whether to delete many or not. Defaults to True.

        Returns:
            int: the number of documents deleted
        """
        return interface.delete(self.vault, parameters, many)

    def query(  # noqa: PLR0913, PLR0917
        self,
        parameters: dict[str, any],
        limit: int = 1000,
        projection: dict | None = None,
        as_gen: bool = False,
        skip: int | None = None,
        use_paginated: bool = False,
        sort: list[tuple] | None = None,
        convert: bool = True,
    ) -> list[any] | Cursor:
        """Searches a collection for documents based on given parameters.

        Parameters should be dictionaries : {key : search}. Where key is an existing key in the collection and
        search is either a value or an expression.
        Expressions can either be {operator: value} or {"$regex": regex_expression}.
        Regex can only be used on string fields.
        Valid operators: https://docs.mongodb.com/manual/reference/operator/query-comparison/
        Parameter examples:
            parameters = {"test_name": "tst_englishUK"}
            parameters = {"test_name": {"$gt": "tst_S"}}
            parameters = {"test_name": {"$regex": "tst_g.*"}}
        Projection examples:
            projection = {"_id": False}.

        Args:
            parameters (dict): parameters to match documents on.
            limit (int, optional): the max number of documents to return. Defaults to 1000.
            projection (dict | None, optional): which keys to return/not return. Defaults to None.
            as_gen (bool, optional): whether to return a Cursor or not. Defaults to False.
            skip (int | None, optional): how many documents to skip. Defaults to None.
            use_paginated (bool, optional): whether to use a paginated response. Defaults to False.
            sort (list[tuple] | None, optional): sort options for the results. Defaults to None.

        Returns:
            list | Cursor: either a list of dataclasses, or a Cursor of the documents
        """
        if projection is not None:
            self._update_projection(projection)

        if as_gen:
            return interface.query(self.vault, parameters, limit, projection, as_gen, skip=skip, sort=sort)
        if use_paginated and not projection:
            return [
                self.make_data_class(data) if convert else data
                for data in self.paginated_query(parameters, limit, skip)
            ]
        return [
            self.make_data_class(data) if convert else data
            for data in interface.query(self.vault, parameters, limit, projection, as_gen, skip=skip, sort=sort)
        ]

    def paginated_query(self, query_dict: dict[str, any], limit: int = 1000, skip: int = 0) -> list[dict[str, any]]:
        """Performs a paginated query with the specified query dict.

        Args:
            query_dict (dict): a dict of query operators
            limit (int): limit of items to retrieve at a time
            skip (int): number of documents to skip at the start

        Returns:
            list[any]: a list of documents from the DB
        """
        docs = []
        len_ret = limit
        while len_ret == limit:
            # keep looping
            ret = interface.query(self.vault, query_dict, lim=limit, projection=None, as_gen=False, skip=skip)
            skip += limit
            len_ret = len(ret)
            docs.extend(ret)
        return [self.make_data_class(doc) for doc in docs]

    def get_collection_names(self) -> list | None:
        """Gets collection names of database.

        Returns:
            None | list: list of names
        """
        return interface.get_collection_names(self.database)

    def create_index(self, field: str) -> bool | str:
        """Creates an index on the current collection.

        Args:
            field (str): field to create an index on

        Returns:
            bool | (str | list): False, or the string
        """
        return interface.create_index(self.vault, field)

    def get_indexes(self) -> list[str]:
        """Gets a list of indexes on the current collection.

        Returns:
            list: list of indexes
        """
        return interface.get_indexes(self.vault)


class NoVaultError(Exception):
    """Custom exception for when we haven't instantiated a vault properly."""

    def __init__(self, message: str) -> None:
        """Initialisation method.

        Args:
            message (str): the message to raise
        """
        super().__init__(message)


class IncorrectDocumentError(Exception):
    """Custom exception for when we haven't got a document formatted correctly."""

    def __init__(self, message: str) -> None:
        """Initialisation method.

        Args:
            message (str): the message to raise
        """
        super().__init__(message)
