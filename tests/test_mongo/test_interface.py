"""Tests our interface.py module."""

from pymongo import MongoClient

from mongo import interface
from mongo.interface import CachedMongoClient
from tests.mocks.mongo_mocks import MockClient, MockCollection, MockDatabase


class TestCachedMongoClient:
    """Tests our CachedMongoClient class."""

    def test_cached_mongo_client(self) -> None:
        """Tests cached mongo client and it's singleton-ness."""
        client = CachedMongoClient("a_connection_string")
        assert isinstance(client.client, MongoClient)

        client2 = CachedMongoClient("a_connection_string")
        assert isinstance(client2.client, MongoClient)

        assert client2 is client
        assert client.client is client2.client


class TestGetClient:
    """Tests out get_client method."""

    def test_get_client_defaults(self) -> None:
        """Tests our get_client method with defaults."""
        client = interface.get_client()
        assert isinstance(client, MongoClient)
        assert interface.get_client() is client

    def test_get_client_with_pw(self) -> None:
        """Tests our get_client method with username/password."""
        client = interface.get_client(user_name="user", password="password")
        assert isinstance(client, MongoClient)
        assert interface.get_client(user_name="user", password="password") is client


class TestClientMethods:
    """Tests our client methods."""

    def test_list_database_names(self) -> None:
        """Tests interface list_database_names method."""
        client = MockClient()
        database_names = interface.get_database_names(client)
        assert isinstance(database_names, list)

    def test_list_collection_names(self) -> None:
        """Tests interface list_collection_names method."""
        database = MockDatabase()
        collection_names = interface.get_collection_names(database)
        assert isinstance(collection_names, list)

    def test_insert_single(self) -> None:
        """Tests interface insert with a single document."""
        collection = MockCollection()
        doc = {"key": "value"}
        result = interface.insert(collection, doc)
        assert isinstance(result, list)

    def test_insert_multiple(self) -> None:
        """Tests interface insert with multiple documents."""
        collection = MockCollection()
        docs = [{"key": f"value{x}"} for x in range(10)]
        result = interface.insert(collection, docs)
        assert isinstance(result, list)

    def test_delete_single(self) -> None:
        """Tests interface delete with not many."""
        collection = MockCollection()
        params = {"key": "value"}
        result = interface.delete(collection, params, many=False)
        assert result == 1

    def test_delete_multiple(self) -> None:
        """Tests interface delete with many."""
        collection = MockCollection()
        params = {"key": "value"}
        result = interface.delete(collection, params, many=True)
        assert result >= 1

    def test_update_single(self) -> None:
        """Tests interface update with not many."""
        collection = MockCollection()
        params = {"key": "value"}
        update = {"$set": {"key": 123}}
        interface.update(collection, params, update, many=False)

    def test_update_multiple(self) -> None:
        """Tests interface update with many."""
        collection = MockCollection()
        params = {"key": "value"}
        update = {"$set": {"key": 123}}
        interface.update(collection, params, update, many=True)

    def test_query_not_list(self) -> None:
        """Tests interface query as not list."""
        collection = MockCollection()
        params = {"key": "value"}
        results = interface.query(collection, params, as_gen=True)
        assert not isinstance(results, list)

    def test_query_list(self) -> None:
        """Tests interface query as list."""
        collection = MockCollection()
        params = {"key": "value"}
        results = interface.query(collection, params, skip=0, as_gen=False)
        assert isinstance(results, list)
