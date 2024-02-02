"""Reminders collection interface."""

import datetime

from bson import ObjectId
from pymongo.results import UpdateResult

from mongo.baseclass import BaseClass
from mongo.datatypes.reminder import ReminderDB


class ServerReminders(BaseClass):
    """Class for interacting with the 'reminders' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method for the class. Initialises the collection object."""
        super().__init__(collection="reminders")

    @staticmethod
    def make_data_class(reminder: dict[str, any]) -> ReminderDB:
        """Converts the reminder into a a dataclass.

        Args:
            reminder (dict): the reminder dictionary

        Returns:
            ReminderDB: the Reminder dataclass
        """
        return ReminderDB(**reminder)

    def get_open_reminders(self, guild_id: int) -> list[ReminderDB]:
        """Get all the currently open reminders for the given guild.

        Args:
            guild_id (int): the guild ID

        Returns:
            list[ReminderDB]: list of reminders
        """
        return self.query({"active": True, "guild_id": guild_id})

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
    ) -> list[ObjectId]:
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
