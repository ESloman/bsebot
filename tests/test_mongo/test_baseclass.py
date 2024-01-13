"""Tests our baseclass.py module."""

import pytest
from pymongo import MongoClient

from mongo.baseclass import BaseClass, IncorrectDocumentError, NoVaultError


class TestBaseClass:
    """Tests our BaseClass class."""

    def test_base_class_init_defaults(self) -> None:
        """Tests BaseClass init with defaults."""
        base_cls = BaseClass()
        assert isinstance(base_cls.mongo_client, MongoClient)
        assert base_cls.cli is BaseClass().mongo_client

    def test_base_class_init(self) -> None:
        """Tests BaseClass init."""
        base_cls = BaseClass("123.0.0.1", username="user", password="pass")
        assert isinstance(base_cls.mongo_client, MongoClient)
        assert base_cls.cli is BaseClass("123.0.0.1", username="user", password="pass").mongo_client

    def test_base_class_bad_user_pass(self) -> None:
        """Tests BaseClass bad user and pass."""
        with pytest.raises(NotImplementedError):
            BaseClass("123.0.0.1", username="", password="")

    def test_base_class_vault_exc(self) -> None:
        """Tests BaseClass vault property raises an exception correctly."""
        base_cls = BaseClass()
        with pytest.raises(NoVaultError, match="No vault instantiated."):
            _ = base_cls.vault

    def test_base_class_vault(self) -> None:
        """Tests BaseClass vault property."""
        base_cls = BaseClass()
        # assign anything to vault
        base_cls._vault = 123
        vault = base_cls.vault
        assert vault is not None

    def test_base_class_update_projection(self) -> None:
        """Tests BaseClass with update_projection."""
        base_cls = BaseClass()
        base_cls._MINIMUM_PROJECTION_DICT = {"_id": True, "guild_id": True, "user_id": True}

        projection = {"user_id": False, "points": True}
        base_cls._update_projection(projection)
        for key, value in base_cls._MINIMUM_PROJECTION_DICT.items():
            assert projection[key] == value

    def test_base_class_update_projection_empty(self) -> None:
        """Tests BaseClass with update_projection and an empty projection."""
        base_cls = BaseClass()
        base_cls._MINIMUM_PROJECTION_DICT = {}

        projection = {"user_id": False, "points": True}
        base_cls._update_projection(projection)

    def test_base_class_make_data_class(self) -> None:
        """Tests BaseClass raises an exception correctly."""
        base_cls = BaseClass()
        with pytest.raises(NotImplementedError):
            base_cls.make_data_class({})

    @pytest.mark.parametrize("doc", [None, "doc", 1234])
    def test_insert_incorrect_document(self, doc: any) -> None:
        """Tests BaseClass insert method with incorrect document."""
        base_cls = BaseClass()
        with pytest.raises(IncorrectDocumentError, match="Given document isn't a dictionary or a list."):
            base_cls.insert(doc)

    @pytest.mark.parametrize("doc", [[None], [{}, None, {}], [123, "doc", {}, {}]])
    def test_insert_incorrect_documents(self, doc: any) -> None:
        """Tests BaseClass insert method with incorrect documents."""
        base_cls = BaseClass()
        with pytest.raises(IncorrectDocumentError, match="Not all documents in the list are dictionaries."):
            base_cls.insert(doc)
