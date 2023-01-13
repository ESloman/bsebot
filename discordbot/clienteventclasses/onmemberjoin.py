import datetime

import discord

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.bot_enums import TransactionTypes, ActivityTypes


class OnMemberJoin(BaseEvent):
    """
    Class for handling when a new member joins the server
    """
    def __init__(self, client, guild_ids, logger):
        super().__init__(client, guild_ids, logger)

    def on_join(self, member: discord.Member) -> None:
        """
        Method for handling when a new member joins the server.
        We basically just make sure that the user has an entry in our DB
        :param member:
        :return: None
        """
        user_id = member.id

        if user := self.user_points.find_user(user_id, member.guild.id):
            self.user_points.update({"_id": user["_id"]}, {"$set": {"inactive": False}})
            self.logger.info(f"Activating BSEddies account for existing user - {user_id} - {member.display_name}")
            self.user_points.append_to_activity_history(
                user_id,
                member.guild.id,
                {
                    "type": ActivityTypes.SERVER_JOIN,
                    "timestamp": datetime.datetime.now()
                }
            )
            return

        self.user_points.create_user(user_id, member.guild.id)

        self.user_points.append_to_transaction_history(
            user_id,
            member.guild.id,
            {
                "type": TransactionTypes.USER_CREATE,
                "amount": 10,
                "timestamp": datetime.datetime.now(),
                "comment": "User created",
            }
        )

        self.user_points.append_to_activity_history(
            user_id,
            member.guild.id,
            {
                "type": ActivityTypes.SERVER_JOIN,
                "timestamp": datetime.datetime.now()
            }
        )

        self.logger.info(f"Creating BSEddies account for new user - {user_id} - {member.display_name}")
