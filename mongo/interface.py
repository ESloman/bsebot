"""Module exists to provide interface methods for our MongoDB client.

We use MongoClient from pymongo. These functions are our abstractions of pre-existing
MongoDB methods.
"""

from urllib.parse import quote_plus

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import UpdateResult

CACHED_CLIENT = None  # type: MongoClient


class CachedMongoClient:
    """Use a singleton class to handle the single MongoClient object that we need to create.

    Returns:
        _type_: CachedMongoClient
    """

    _instance = None
    _client = None

    def __new__(cls: "CachedMongoClient", _: str) -> "CachedMongoClient":
        """Instantantiation method.

        Returns:
            CachedMongoClient: either the existing class or a new one
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self: "CachedMongoClient", connection: str) -> None:
        """Initialisation method.

        Args:
            connection (str): the connection string for the MongoClient
        """
        if not self._client:
            self._client = MongoClient(connection, serverSelectionTimeoutMS=1000, tz_aware=True)

    @property
    def client(self: "CachedMongoClient") -> MongoClient:
        """The underlying MongoClient.

        Returns:
            MongoClient: the client
        """
        return self._client


def get_client(
    ip: str = "127.0.0.1",
    user_name: str | None = None,
    password: str | None = None,
    port: str = "27017",
) -> MongoClient | bool:
    """Returns the MongoDB Client connection for interacting with MongoDB Database Objects.

    Args:
        ip (str): IP address of server to connect to. Defaults to 127.0.0.1.
        user_name (str | None): user name to login to instance with. Defaults to None.
        password (str | None): password to login to instance with. Defaults to None.
        port (str): the port to connect to. Defaults to 27017.

    Returns:
        bool | MongoClient: either False, of the MongoClient
    """
    if user_name is None and password is None:
        connection = f"mongodb://{ip}:{port}"
    elif user_name and password:
        u = quote_plus(user_name)
        p = quote_plus(password)
        connection = f"mongodb://{u}:{p}@{ip}:{port}"
    else:
        raise NotImplementedError
    client_cls = CachedMongoClient(connection)
    return client_cls.client


def get_database_names(client: MongoClient) -> list[str]:
    """Returns a list of database names for a given client.

    Args:
        client (MongoClient): the mongo Client

    Returns:
        list[str]: list of database names
    """
    return client.list_database_names()


def get_database(client: MongoClient, database: str) -> Database:
    """Returns a mongoDB object for a given client and database.

    If the database doesn't exist, this will create a new database for the client.

    Args:
        client (MongoClient): object to get database from
        database (str): of database name to get

    Returns:
        Database: the Database object
    """
    return client[database]


def get_collection_names(database: Database, include_system_collections: bool = False) -> list[str]:
    """Returns a list of collections for a given mongoDB database.

    Args:
        database (Database): pymongo Database object
        include_system_collections (bool): whether or not to include the system collections

    Returns:
        list[str]: list of collection names
    """
    return database.list_collection_names(include_system_collections=include_system_collections)


def get_collection(database: Database, collection: str) -> Collection:
    """Returns a mongoDB collection object for a given database and collection name.

    If the collection doesn't exist, this will create it.

    Args:
        database (Database): pymongo Database object
        collection (str): name of collection to get

    Returns:
        Collection: the collection object
    """
    return database[collection]


def insert(
    collection: Collection,
    documents: list[dict[str, any]] | dict[str, any],
    in_order: bool = True,
) -> list[ObjectId]:
    """Inserts a given number of documents into a given collection.

    Returns a list of objectIDs of the items inserted.

    Args:
        collection (Collection): a mongoDB collection object
        documents (list | dict): the document(s) to insert
        in_order (bool): whether the documents should be entered serially

    Returns:
        list[ObjectId]: list of inserted IDs
    """
    documents = (
        [
            documents,
        ]
        if isinstance(documents, dict)
        else documents
    )
    results = collection.insert_many(documents, ordered=in_order)
    return results.inserted_ids


def delete(collection: Collection, params: dict[str, any], many: bool = True) -> int:
    """Deletes all documents matching the query from the database.

    Args:
        collection (Collection): a mongoDB collection object
        params (dict[str, any]): A dict to match eg {"status": "Pass"}
        many (bool): whether to delete more than one. Defaults to True.

    Returns:
        int: number of docs deleted
    """
    delete_func = collection.delete_many if many else collection.delete_one
    return delete_func(params).deleted_count


def update(
    collection: Collection,
    parameters: dict[str, any],
    updated_vals: dict[str, any],
    many: bool = True,
    upsert: bool = False,
) -> UpdateResult:
    """Searches and updates for matching entries based on a given parameters.

    Parameters should be a dictionary of collection keys and values. See interface.query for more information regarding
    search parameters.
    Update should also be a dictionary where the keys are update operators and the values are dictionaries of
    {col_key: value_to_apply}.
    See the following specifications for more information.
    http://api.mongodb.com/python/current/api/pymongo/operations.html#pymongo.operations.UpdateOne
    https://docs.mongodb.com/manual/reference/method/db.collection.updateOne/
    https://docs.mongodb.com/manual/reference/operator/update/.

    Args:
        collection (Collection): mongoDB collection object
        parameters (dict[str, any]): dictionary of search parameters
        updated_vals (dict[str, any): dict of update operators and values to apply
        many (bool): whether to update many docs at once. Defaults to True.
        upsert (bool): whether to create new parameters. Defaults to False.

    Returns:
        UpdateResult: the update result
    """
    update_func = collection.update_many if many else collection.update_one
    # noinspection PyArgumentList
    return update_func(filter=parameters, update=updated_vals, upsert=upsert)


def query(  # noqa: PLR0913, PLR0917
    collection: Collection,
    parameters: dict[str, any],
    lim: int = 10000,
    projection: dict | None = None,
    as_gen: bool = True,
    skip: int | None = None,
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
        collection (Collection): collection object to query
        parameters (dict): dictionary as above
        lim (int): max number of results to return
        projection (dict | None): dict of keys to return for each result
        as_gen (bool): True returns generator (mongoDB cursor obj) and false returns list of results
        skip (int | None): how many items to skip
        sort (list[tuple] | None): what to sort the items on

    Returns:
        list | Cursor: a generator (cursor obj) if as_gen else returns a list of results.
    """
    if skip is None:
        skip = 0
    results = collection.find(parameters, limit=lim, projection=projection, skip=skip, sort=sort)
    return results if as_gen else list(results)


def drop_collection(name_or_collection: str | Collection, database: Database = None) -> bool:
    """Drops a given collection.

    NON REVERSIBLE. The given collection can be a collection object or the name of the
    collection. If it's a name, the database object must be provided too. Returns True if valid or False if input
    parameters were incorrect.

    Args:
        name_or_collection (str): name of collection or Collection object
        database (Database): Database object

    Returns:
        bool: whether it succeeded or not
    """
    if database is None and isinstance(name_or_collection, Collection):
        name_or_collection.drop()
        return True
    if database is not None and isinstance(database, Database):
        database.drop_collection(name_or_collection)
        return True
    return False


def create_index(collection: Collection, key_or_list_of_keys_to_index: str | list) -> bool | (list | str):
    """Creates an index for a given collection for the given key(s).

    Docs: https://docs.mongodb.com/manual/indexes/#index-types

    Args:
        collection (Collection): the collection to create an index for
        key_or_list_of_keys_to_index (str | list): either the index, or list of indices, to create an index for.

    Returns:
        bool | (list | str): either False, or the index information
    """
    if not collection:
        return False
    if not isinstance(key_or_list_of_keys_to_index, list):
        key_or_list_of_keys_to_index = [
            key_or_list_of_keys_to_index,
        ]
    rets = [collection.create_index(key_to_index) for key_to_index in key_or_list_of_keys_to_index]
    return rets if len(rets) > 1 else rets[0]


def get_indexes(collection: Collection) -> dict[str, any] | bool:
    """Returns the indexes for the given collection.

    Args:
        collection (Collection): the collection object to get indices for.

    Returns:
        dict[str, any] | bool: either False, or the index information
    """
    if not collection:
        return False
    return collection.index_information()
