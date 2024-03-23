"""Stats slash command."""

import datetime
import re
from zoneinfo import ZoneInfo

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.constants import WORDLE_SCORE_REGEX
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.stats.statsdatacache import StatsDataCache
from discordbot.stats.statsdataclasses import StatsData
from discordbot.views.stats import StatsView
from mongo.datatypes.message import MessageDB


class Stats(BSEddies):
    """Class for handling `/stats` commands."""

    def __init__(self, client: BSEBot, guild_ids: list[int]) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs

        """
        super().__init__(client, guild_ids)
        self.activity_type = ActivityTypes.STATS
        self.help_string = "View some stats"
        self.command_name = "stats"

    @staticmethod
    def _do_message_counts(messages: list[MessageDB]) -> dict[str, any]:  # noqa: C901, PLR0915
        _swears = ["fuck", "shit", "cunt", "piss", "cock", "bollock", "dick", "twat"]

        _dict = {}

        _lengths = []
        _words = []
        _channels_dict = {}
        _users_dict = {}
        _swears_dict = dict.fromkeys(_swears, 0)

        # these two should only be different when NOT in server mode
        _replies_count = 0  # how many times this user received a reply
        _replied_count = 0  # how many times this user replied to someone

        _wordle_scores = []

        for message in messages:
            _channel_id = message.channel_id
            if _channel_id not in _channels_dict:
                _channels_dict[_channel_id] = 0
            _channels_dict[_channel_id] += 1

            if "message" in message.message_type:
                uid = message.user_id
                if uid not in _users_dict:
                    _users_dict[uid] = 0
                _users_dict[uid] += 1

            # replies
            if "reply" in message.message_type:
                _replied_count += 1
            _replies_count += len(message.replies)

            if content := message.content:
                _lengths.append(len(content))
                _words.append(len(content.split(" ")))

                if "wordle" in message.message_type:
                    result = re.search(WORDLE_SCORE_REGEX, content).group()
                    guesses = result.split("/")[0]

                    if guesses == "X":
                        guesses = "10"
                    guesses = int(guesses)
                    _wordle_scores.append(guesses)

                # count swears
                for swear in _swears:
                    _swears_dict[swear] += content.count(swear)

        top_channels = sorted(_channels_dict, key=lambda x: _channels_dict[x], reverse=True)
        top_five_channels = [
            (_chan, _channels_dict[_chan])
            for _chan in top_channels[: 5 if len(top_channels) > 5 else -1]  # noqa: PLR2004
        ]

        top_swears = sorted(_swears_dict, key=lambda x: _swears_dict[x], reverse=True)
        top_three_swears = [(_swear, _swears_dict[_swear]) for _swear in top_swears[:3] if _swears_dict[_swear]]

        top_users = sorted(_users_dict, key=lambda x: _users_dict[x], reverse=True)
        top_five_users = [
            (_user, _users_dict[_user])
            for _user in top_users[: 5 if len(top_users) > 5 else -1]  # noqa: PLR2004
        ]

        _dict["top_five"] = top_five_channels
        _dict["average_length"] = round((sum(_lengths) / len(_lengths)), 2)
        _dict["average_word_count"] = round((sum(_words) / len(_words)), 2)
        _dict["total_swears"] = sum(_swears_dict.values())
        _dict["top_swears"] = top_three_swears
        _dict["replies_count"] = _replies_count
        _dict["replied_count"] = _replied_count
        _dict["top_users"] = top_five_users
        _dict["wordles"] = len(_wordle_scores)

        try:
            _dict["average_wordle_score"] = round((sum(_wordle_scores) / len(_wordle_scores)), 2)
        except ZeroDivisionError:
            _dict["average_wordle_score"] = 0.0

        return _dict

    async def create_stats_view(self, ctx: discord.ApplicationContext) -> None:
        """Creates the view.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.defer(ephemeral=True)

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.STATS)

        _view = StatsView(self)
        _msg = "# Stats\nSelect stats generation method."

        await ctx.followup.send(content=_msg, view=_view, ephemeral=True)

    async def stats_quick(self, interaction: discord.Interaction) -> None:
        """_summary_.

        Args:
            interaction (discord.Interaction): _description_
        """
        await interaction.response.defer(ephemeral=True)

        # general summary of messages

        total, monthly = self._stats(interaction, False)

        message = (
            f"# {interaction.user.display_name}'s Quick Stats\n"
            "Quick all time stats - numbers in parentheses (where applicable) are this month's for comparison.\n\n"
            "## Messages\n"
            f"- **Total**: {total.total_messages} ({monthly.total_messages})\n"
            f"- **Average Length**: {total.average_length} ({monthly.average_length})\n"
            f"- **Average Word Count**: {total.average_words} ({monthly.average_words})\n"
            "- **All time top channels**:"
        )

        for channel in total.top_channels:
            message += f"\n - <#{channel[0]}>: {channel[1]}"

        message += "\n- **This month's top channels**:"
        for channel in monthly.top_channels:
            message += f"\n - <#{channel[0]}>: {channel[1]}"

        message += (
            "\n"
            f"- **Messages you _replied_ to**: {total.replied_count} ({monthly.replied_count})\n"
            f"- **Replies _received_**: {total.replies_count} ({monthly.replies_count})\n"
            f"- **Total Swears**: {total.total_swears} ({monthly.total_swears})\n"
            "- **Top swears**:"
        )

        if total.total_swears:
            for swear in total.top_swears:
                message += f"\n - `{swear[0]}`: {swear[1]}"

            message += "\n- **This month's top swears**:"
            for swear in monthly.top_swears:
                message += f"\n - `{swear[0]}`: {swear[1]}"

        # wordle stuff
        app_command = next(app_com for app_com in self.client.application_commands if app_com.name == "wordle")

        message += (
            "\n\n"
            "## Wordle\n"
            f"- **Completed wordles count**: {total.wordles} ({monthly.wordles})\n"
            f"- **Average wordle score**: {total.average_wordle_score} ({monthly.average_wordle_score})\n"
            "\n"
            f"For more Wordle stats - use {app_command.mention}."
        )

        self.logger.info("Stats message length: %s", len(message))

        await interaction.followup.send(content=message, ephemeral=True)

    async def stats_server(self, interaction: discord.Interaction) -> None:
        """Calculates stats.

        Args:
            interaction (discord.Interaction): the interaction
        """
        await interaction.response.defer(ephemeral=True)
        total, monthly = self._stats(interaction, True)

        # messages

        message = (
            f"# {interaction.guild.name}'s Quick Stats\n"
            "Quick all time stats - numbers in parentheses (where applicable) are this month's for comparison.\n\n"
            "## Messages\n"
            f"- **Total**: {total.total_messages} ({monthly.total_messages})\n"
            f"- **Average Length**: {total.average_length} ({monthly.average_length})\n"
            f"- **Average Word Count**: {total.average_words} ({monthly.average_words})\n"
            "- **All time top users**:"
        )

        for user in total.top_users:
            message += f"\n - <@{user[0]}>: {user[1]}"

        message += "\n- **This month's top users**:"
        for user in monthly.top_users:
            message += f"\n - <@{user[0]}>: {user[1]}"

        message += "\n- **All time top channels**:"
        for channel in total.top_channels:
            message += f"\n - <#{channel[0]}>: {channel[1]}"

        message += "\n- **This month's top channels**:"
        for channel in monthly.top_channels:
            message += f"\n - <#{channel[0]}>: {channel[1]}"

        message += (
            "\n"
            f"- **Total Replies**: {total.replies_count} ({monthly.replies_count})\n"
            f"- **Total Swears**: {total.total_swears} ({monthly.total_swears})\n"
            "- **Top swears**:"
        )

        if total.total_swears:
            for swear in total.top_swears:
                message += f"\n - `{swear[0]}`: {swear[1]}"

            message += "\n- **This month's top swears**:"
            for swear in monthly.top_swears:
                message += f"\n - `{swear[0]}`: {swear[1]}"

        # wordle stuff
        app_command = next(app_com for app_com in self.client.application_commands if app_com.name == "wordle")

        message += (
            "\n\n"
            "## Wordle\n"
            f"- **Completed wordles count**: {total.wordles} ({monthly.wordles})\n"
            f"- **Average wordle score**: {total.average_wordle_score} ({monthly.average_wordle_score})\n"
            "\n"
            f"For more Wordle stats - use {app_command.mention}."
        )

        self.logger.info("Stats message length: %s", len(message))

        await interaction.followup.send(content=message, ephemeral=True)

    def _stats(self, interaction: discord.Interaction, server: bool = False) -> tuple[StatsData, StatsData]:
        """Generates a generic 'StatsData' class with stats on either a user, or a server.

        Args:
            interaction (discord.Interaction): the discord interaction
            server (bool, optional): True is server wide, False if user specific. Defaults to False.

        Returns:
            tuple[StatsData, StatsData]: a tuple of Stats Data, all time stats and this month's stats
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        start = now.replace(year=2012, month=1, day=1, hour=1, second=1, microsecond=1)
        end = start.replace(year=now.year + 1)

        month_start = now.replace(day=1, hour=0, minute=0, second=0)
        try:
            month_end = month_start.replace(month=now.month + 1)
        except ValueError:
            month_end = month_start.replace(month=1, year=now.year + 1)

        _guild_id = interaction.guild_id

        _cache = StatsDataCache(uid=interaction.user.id if not server else None)

        # messages
        messages = _cache.get_messages(_guild_id, start, end)
        monthly_messages = [m for m in messages if month_start <= m.timestamp <= month_end]

        total_messages = len(messages)
        monthly_total_messages = len(monthly_messages)

        # start the count
        counts = self._do_message_counts(messages)
        monthly_counts = self._do_message_counts(monthly_messages)

        # create dataclasses
        total_stats = StatsData(
            total_messages=total_messages,
            top_channels=counts["top_five"],
            average_length=counts["average_length"],
            average_words=counts["average_word_count"],
            total_swears=counts["total_swears"],
            top_swears=counts["top_swears"],
            replied_count=counts["replied_count"],
            replies_count=counts["replies_count"],
            top_users=counts["top_users"],
            wordles=counts["wordles"],
            average_wordle_score=counts["average_wordle_score"],
        )

        monthly_stats = StatsData(
            total_messages=monthly_total_messages,
            top_channels=monthly_counts["top_five"],
            average_length=monthly_counts["average_length"],
            average_words=monthly_counts["average_word_count"],
            total_swears=monthly_counts["total_swears"],
            top_swears=monthly_counts["top_swears"],
            replied_count=monthly_counts["replied_count"],
            replies_count=monthly_counts["replies_count"],
            top_users=monthly_counts["top_users"],
            wordles=monthly_counts["wordles"],
            average_wordle_score=monthly_counts["average_wordle_score"],
        )

        return total_stats, monthly_stats
