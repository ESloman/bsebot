"""This file is for DB classes.

A DB class represents a MongoDB Database object.
A DB class derives from a 'BaseClass' which will represent a MongoClient object.
The DB class will provide methods shared between all Collection Classes that we will need.

Each DB in Mongo that we're interacting with should have a 'DB Class' in this file. Each Collection in that database
should have a Collection class in another file that inherits from this DB class.
"""

from pymongo.database import Database

from mongo import interface
from mongo.baseclass import BaseClass


class BestSummerEverPointsDB(BaseClass):
    """Class to represent the BestSummerEverPoints DB."""

    def __init__(self) -> None:
        """Constructor method that initialises the DB object."""
        super().__init__()
        self.bse_db = interface.get_database(self.cli, "bestsummereverpoints")

    @property
    def database(self) -> Database:
        """Basic database property.

        Returns:
            Database: the database
        """
        return self.bse_db


class BestSummerEverGameServersDB(BaseClass):
    """Class to represent the BestSummerEverGameServers DB."""

    def __init__(self) -> None:
        """Constructor method that initialises the DB object."""
        super().__init__()
        self.bse_servers_db = interface.get_database(self.cli, "bestsummerevergameservers")

    @property
    def database(self) -> Database:
        """Basic database property.

        Returns:
            Database: the database
        """
        return self.bse_servers_db


class BestSummerEverWordleDB(BaseClass):
    """Class to represent the BestSummereverWordle DB."""

    def __init__(self) -> None:
        """Constructor method that initialises the DB object."""
        super().__init__()
        self.bse_servers_db = interface.get_database(self.cli, "bestsummereverwordle")

    @property
    def database(self) -> Database:
        """Basic database property.

        Returns:
            Database: the database
        """
        return self.bse_servers_db
