"""Mongo baseclass."""

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.results import InsertManyResult, InsertOneResult, UpdateResult

from mongo import interface


class BaseClass:
    """Base MongoDB DB Class.

    Provides basic method and properties that all other DB Classes will need.
    If not username or password is provided - authenticate without username and password.
    """

    _MINIMUM_PROJECTION_DICT: dict | None = None

    def __init__(self, ip: str = "127.0.0.1", username: str | None = None, password: str | None = None) -> None:
        """Initialisation method.

        Args:
            ip (str, optional): ip to connect to. Defaults to "127.0.0.1".
            username (str | None, optional): username. Defaults to None.
            password (str | None, optional): password. Defaults to None.
        """
        self.cli = interface.get_client(ip, username, password)
        self._vault = None

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

        Returns:
            Collection: the collection/vault
        """
        return self._vault

    @property
    def minimum_projection(self) -> dict | None:
        """Minimum projection property.

        Returns:
            dict | None: None, or the minimum projection
        """
        return self._MINIMUM_PROJECTION_DICT

    def update_projection(self, projection: dict) -> None:
        """Updates the given projection with the minimum values defined.

        Args:
            projection (dict): _description_
        """
        if not self.minimum_projection:
            return
        projection.update(self.minimum_projection)

    def insert(self, document: dict | list) -> InsertOneResult | InsertManyResult:
        """Inserts the given object into this class' Collection object.

        Args:
            document (dict | list): the document or list of documents to insert

        Raises:
            NoVaultError: _description_
            IncorrectDocument: _description_
            IncorrectDocument: _description_

        Returns:
            InsertOneResult | InsertManyResult: _description_
        """
        if self.vault is None:
            msg = "No vault instantiated."
            raise NoVaultError(msg)
        if not isinstance(document, list | dict):
            msg = "Given document isn't a dictionary or a list."
            raise IncorrectDocumentError(msg)

        if isinstance(document, list) and not all(isinstance(k, dict) for k in document):
            msg = "Not all documents in the list are dictionaries."
            raise IncorrectDocumentError(msg)
        return interface.insert(self._vault, document)

    def update(self, parameters: dict, updated_vals: dict, many: bool = False) -> UpdateResult:
        """Updates all documents based on the given parameters with the provided values.

        Args:
            parameters (dict): _description_
            updated_vals (dict): _description_
            many (bool, optional): _description_. Defaults to False.

        Raises:
            NoVaultError: _description_

        Returns:
            UpdateResult: _description_
        """
        if self.vault is None:
            msg = "No vault instantiated."
            raise NoVaultError(msg)
        return interface.update(self.vault, parameters, updated_vals, many)

    def delete(self, parameters: dict, many: bool = True) -> int:
        """Deletes documents based on the given parameters. If many=False, only deletes one else it deletes all matches.

        Args:
            parameters (dict): _description_
            many (bool, optional): _description_. Defaults to True.

        Raises:
            NoVaultError: _description_

        Returns:
            int: _description_
        """
        if self.vault is None:
            msg = "No vault instantiated."
            raise NoVaultError(msg)
        return interface.delete(self.vault, parameters, many)

    def query(  # noqa: PLR0913, PLR0917
        self,
        parameters: dict,
        limit: int = 1000,
        projection: dict | None = None,
        as_gen: bool = False,
        skip: int | None = None,
        use_paginated: bool = False,
        sort: list[tuple] | None = None,
    ) -> list | Cursor:
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
            parameters (dict): _description_
            limit (int, optional): _description_. Defaults to 1000.
            projection (dict | None, optional): _description_. Defaults to None.
            as_gen (bool, optional): _description_. Defaults to False.
            skip (int | None, optional): _description_. Defaults to None.
            use_paginated (bool, optional): _description_. Defaults to False.
            sort (list[tuple] | None, optional): _description_. Defaults to None.

        Raises:
            NoVaultError: _description_

        Returns:
            list | Cursor: _description_
        """
        if self.vault is None:
            msg = "No vault instantiated."
            raise NoVaultError(msg)
        if not projection or as_gen or not use_paginated:
            return interface.query(self.vault, parameters, limit, projection, as_gen, skip=skip, sort=sort)
        return self.paginated_query(parameters, limit, skip)

    def paginated_query(self, query_dict: dict, limit: int = 1000, skip: int = 0) -> list[dict]:
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
        return docs

    def get_collection_names(self) -> None | list:
        """Gets collection names of database.

        Raises:
            NoVaultError: _description_

        Returns:
            None | list: _description_
        """
        if not hasattr(self, "database"):
            msg = "No vault instantiated."
            raise NoVaultError(msg)
        return interface.get_collection_names(self.database)

    def create_index(self, field: str) -> bool | (str | list):
        """Creates an index on the current collection.

        Args:
            self (_type_): _description_

        Raises:
            NoVaultError: _description_

        Returns:
            _type_: _description_
        """
        if self.vault is None:
            msg = "No vault instantiated."
            raise NoVaultError(msg)
        return interface.create_index(self.vault, field)

    def get_indexes(self) -> list:
        """Gets a list of indexes on the current collection.

        Raises:
            NoVaultError: _description_

        Returns:
            list: _description_
        """
        if self.vault is None:
            msg = "No vault instantiated."
            raise NoVaultError(msg)
        return interface.get_indexes(self.vault)


class NoVaultError(Exception):
    """Custom exception for when we haven't instantiated a vault properly."""

    def __init__(self, message: str) -> None:
        """Initialisation method.

        Args:
            message (str): _description_
        """
        super().__init__(message)


class IncorrectDocumentError(Exception):
    """Custom exception for when we haven't got a document formatted correctly."""

    def __init__(self, message: str) -> None:
        """Initialisation method.

        Args:
            message (str): _description_
        """
        super().__init__(message)
