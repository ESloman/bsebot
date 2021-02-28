import datetime
import discord

from discordbot.baseeventclass import BaseEvent
from discordbot.bot_enums import TransactionTypes
from discordbot.constants import THE_BOYS_ROLE
from discordbot.reactioneventclasses import BetReactionEvent, LeaderBoardReactionEvent
from mongo.bsepoints import UserInteractions


class OnReadyEvent(BaseEvent):
    """
    Class for handling on_ready event
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    async def on_ready(self) -> None:
        """
        Method called for on_ready event. Makes sure we have an entry for every user in each guild.
        :return: None
        """
        self.logger.info("Checking guilds for members")

        for guild_id in self.guild_ids:
            guild = self.client.get_guild(guild_id)
            self.logger.info(f"Checking guild: {guild.id} - {guild.name}")
            for member in guild.members:  # type: discord.Member
                if member.bot:
                    continue

                self.logger.info(f"Checking {member.id} - {member.name}")
                user = self.user_points.find_user(member.id, guild.id)
                if not user:

                    the_boys_role = [role for role in member.roles if role == THE_BOYS_ROLE]

                    self.user_points.create_user(member.id, guild.id, bool(the_boys_role))
                    self.logger.info(
                        f"Creating new user entry for {member.id} - {member.name} for {guild.id} - {guild.name}"
                    )

                    self.user_points.append_to_transaction_history(
                        member.id,
                        guild.id,
                        {
                            "type": TransactionTypes.USER_CREATE,
                            "amount": 10,
                            "timestamp": datetime.datetime.now(),
                            "comment": "User created",
                        }
                    )
                    continue

                if not user.get("daily_eddies"):
                    the_boys_role = [role for role in member.roles if role == THE_BOYS_ROLE]
                    self.user_points.set_daily_eddies_toggle(member.id, guild.id, bool(the_boys_role))

        self.logger.info("Finished member check.")


class OnMemberJoin(BaseEvent):
    """
    Class for handling when a new member joins the server
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    def on_join(self, member: discord.Member) -> None:
        """
        Method for handling when a new member joins the server.
        We basically just make sure that the user has an entry in our DB
        :param member:
        :return: None
        """
        user_id = member.id
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

        self.logger.info(f"Creating BSEddies account for new user - {user_id} - {member.display_name}")


class OnReactionAdd(BaseEvent):
    """
    Class for handling on_reaction_add events from Discord
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.leadership_event = LeaderBoardReactionEvent(client, guild_ids, logger, beta_mode=beta_mode)
        self.bet_event = BetReactionEvent(client, guild_ids, logger, beta_mode=beta_mode)

    async def handle_reaction_event(
            self,
            message: discord.Message,
            guild: discord.Guild,
            channel: discord.TextChannel,
            reaction_emoji: str,
            user: discord.User
    ) -> None:
        """
        Main event for handling reaction events.

        Firstly, we only care about reactions if they're from users so we discard any bot reactions.

        Secondly, we only care about reactions to bot messages at the moment so discard any other events.

        Then we check what type of message the user is reacting to and pass it off to the relevant class to handle
        the event

        :param message:
        :param guild:
        :param channel:
        :param reaction_emoji:
        :param user:
        :return:
        """
        if user.bot:
            return

        if guild.id not in self.guild_ids:
            return

        if not message.author.bot:
            return

        # handling leaderboard messages
        if message.content and "BSEddies Leaderboard" in message.content and reaction_emoji == u"▶️":
            await self.leadership_event.handle_leaderboard_reaction(message, guild)
            return

        # handling reactions to BETS
        if message.embeds and "Bet ID" in message.embeds[0].description:
            await self.bet_event.handle_bet_reaction_event(message, guild, channel, reaction_emoji, user)
            return


class OnMessage(BaseEvent):
    """
    Class for handling on_message events from Discord
    """

    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.user_interactions = UserInteractions()

    async def message_received(self, message: discord.Message):
        """
        Main method for handling when we receive a message.
        Mostly just extracts data and puts it into the DB.
        We also work out what "type" of message it is.
        :param message:
        :return:
        """

        guild_id = message.guild.id
        user_id = message.author.id
        channel_id = message.channel.id
        message_content = message.content

        if guild_id not in self.guild_ids:
            return

        if message.reference:
            message_type = "reply"
        elif message.attachments:
            message_type = "attachment"
        elif message.role_mentions:
            message_type = "role_mention"
        elif message.channel_mentions:
            message_type = "channel_mention"
        elif message.mentions:
            message_type = "mention"
        elif message.mention_everyone:
            message_type = "everyone_mention"
        elif "https://" in message.content or "http://" in message_content:
            if "gif" in message.content:
                message_type = "gif"
            else:
                message_type = "link"
        else:
            message_type = "message"

        self.user_interactions.add_entry(
            message.id,
            guild_id,
            user_id,
            channel_id,
            message_type,
            message_content,
            message.created_at
        )
