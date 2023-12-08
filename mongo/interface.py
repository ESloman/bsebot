"""Module exists to provide interface methods for our MongoDB client.

We use MongoClient from pymongo. These functions are our abstractions of pre-existing
MongoDB methods.
"""

from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertManyResult, InsertOneResult, UpdateResult

CACHED_CLIENT = None  # type: MongoClient


class CachedMongoClient:
    """Use a singleton class to handle the single MongoClient object that we need to create.

    Returns:
        _type_: CachedMongoClient
    """

    _instance = None
    _client = None

    def __new__(cls: "CachedMongoClient") -> "CachedMongoClient":
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
            self._client = MongoClient(
                connection,
                serverSelectionTimeoutMS=1000,
            )

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

    :param ip: STR - IP address of mongo instance to get client for
    :param user_name: STR - user name to login to instance with
    :param password: STR - password to login to instance with

    :returns MongoClient object:
    """
    if user_name is None and password is None:
        connection = f"mongodb://{ip}:{port}"
    elif user_name and password:
        u = quote_plus(user_name)
        p = quote_plus(password)
        connection = f"mongodb://{u}:{p}@{ip}:{port}"
    else:
        return False
    client_cls = CachedMongoClient(connection)
    return client_cls.client


def get_database_names(client: MongoClient) -> list:
    """Returns a list of database names for a given client.

    :param client: MongoClient object to return database names of

    :returns list of database names:
    """
    return client.list_database_names()


def get_database(client: MongoClient, database: str) -> Database:
    """Returns a mongoDB object for a given client and database.

    If the database doesn't exist, this will create a new database for the client.

    :param client: MongoClient object to get database from
    :param database: str of database name to get

    :returns pymongo Database object:
    """
    return client[database]


def get_collection_names(database: Database, include_system_collections: bool = False) -> list:
    """Returns a list of collections for a given mongoDB database.

    :param database: pymongo Database object
    :param include_system_collections: bool. Whether or not to include the system collections

    :returns list of collections in database:
    """
    return database.list_collection_names(include_system_collections=include_system_collections)


def get_collection(database: Database, collection: str) -> Collection:
    """Returns a mongoDB collection object for a given database and collection name.

    If the collection doesn't exist, this will create it.

    :param database: pymongo Database object
    :param collection: str name of collection to get

    :returns pymongo Collection object:
    """
    return database[collection]


def insert(
    collection: Collection,
    documents: list | dict,
    in_order: bool = True,
) -> InsertOneResult | InsertManyResult:
    """Inserts a given number of documents into a given collection.

    Returns a list of objectIDs of the items inserted.

    Args:
        collection : a mongoDB collection object
        documents : either a single document in dict form, or a list of documents as a list of dicts
        in_order : whether the documents should be entered in serial.

    :returns: list of inserted IDs
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


def delete(collection: Collection, params: dict, many: bool = True) -> int:
    """Deletes all documents matching the query from the database.

    Returns the number of documents deleted
    Args:
        collection : a mongoDB collection object
        params : A dict to match eg {"status": "Pass"}
        many : delete all matching if True, else delete first found.

    :returns: int of deleted entries
    """
    delete_func = collection.delete_many if many else collection.delete_one
    return delete_func(params).deleted_count


def update(
    collection: Collection,
    parameters: dict,
    updated_vals: dict,
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
        collection : mongoDB collection object
        parameters : dictionary as above
        updated_vals : dict of update operators and values to apply
        many : bool, if True then update all matching docs, if False then update first found doc
        upsert: bool, if True then function will create an entry matching the parameters if one doesn't exist.
    Returns result object.
    """
    update_func = collection.update_many if many else collection.update_one
    # noinspection PyArgumentList
    return update_func(filter=parameters, update=updated_vals, upsert=upsert)


def query(  # noqa: PLR0913, PLR0917
    collection: Collection,
    parameters: dict,
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
        collection : collection object to query
        parameters : dictionary as above
        lim : max number of results to return
        projection : dict of keys to return for each result
        as_gen : True returns generator (mongoDB cursor obj) and false returns list of results
    Returns a generator (cursor obj) if as_gen else returns a list of results.
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
    :param name_or_collection: str name of collection or Collection object
    :param database: Database object
    :return: bool.
    """
    if database is None and type(name_or_collection) is Collection:
        name_or_collection.drop()
        return True
    if type(database) is Database:
        database.drop_collection(name_or_collection)
        return True
    return False


def create_index(collection: Collection, key_or_list_of_keys_to_index: str | list) -> bool | (list | str):
    """Creates an index for a given collection for the given key(s).

    Docs: https://docs.mongodb.com/manual/indexes/#index-types
    :param collection:
    :param key_or_list_of_keys_to_index:
    :return:
    """
    if not collection:
        return False
    if not isinstance(key_or_list_of_keys_to_index, list):
        key_or_list_of_keys_to_index = [
            key_or_list_of_keys_to_index,
        ]
    rets = [collection.create_index(key_to_index) for key_to_index in key_or_list_of_keys_to_index]
    return rets if len(rets) > 1 else rets[0]


def get_indexes(collection: Collection) -> dict[str, any]:
    """Returns the indexes for the given collection.

    :param collection:
    :return:
    """
    if not collection:
        return False
    return collection.index_information()
