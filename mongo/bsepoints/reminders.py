"""Reminders collection interface."""

import datetime

from bson import ObjectId
from pymongo.results import UpdateResult

from mongo import interface
from mongo.datatypes.reminder import ReminderDB
from mongo.db_classes import BestSummerEverPointsDB


class ServerReminders(BestSummerEverPointsDB):
    """Class for interacting with the 'reminders' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method for the class. Initialises the collection object."""
        super().__init__()
        self._vault = interface.get_collection(self.database, "reminders")

    def get_open_reminders(self, guild_id: int) -> list[ReminderDB]:
        """Get all the currently open reminders for the given guild.

        :param guild_id:
        :return:
        """
        ret = self.query({"active": True, "guild_id": guild_id})
        return [ReminderDB(**reminder) for reminder in ret]

    def close_reminder(self, object_id: ObjectId) -> UpdateResult:
        """Closes a reminder.

        Args:
            object_id (ObjectId): objectID of the reminder

        Returns:
            UpdateResult: update result
        """
        return self.update({"_id": object_id}, {"$set": {"active": False}})

    def insert_reminder(  # noqa: PLR0913, PLR0917
        self,
        guild_id: int,
        user_id: int,
        created: datetime.datetime,
        timeout: datetime.datetime,
        reason: str,
        channel_id: int,
        message_id: int,
    ) -> list:
        """Inserts a reminder into the database.

        Args:
            guild_id (int): guild ID the reminder exists in
            user_id (int): the user ID who triggered the reminder
            created (datetime.datetime): when the reminder was created
            timeout (datetime.datetime): when we should remind the user
            reason (str): the reason the user gave for the reminder
            channel_id (int): the channel ID we sent with reminder details
            message_id (int): the message ID we sent with reminder details
        """
        doc = {
            "created": created,
            "user_id": user_id,
            "guild_id": guild_id,
            "reason": reason,
            "timeout": timeout,
            "channel_id": channel_id,
            "message_id": message_id,
            "active": True,
        }

        return self.insert(doc)
