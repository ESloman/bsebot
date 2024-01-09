"""Tests our interface.py module."""

from pymongo import MongoClient

from mongo import interface
from mongo.interface import CachedMongoClient


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
