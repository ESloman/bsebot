"""Contains our EmbedManager class."""

import datetime
from logging import Logger

import discord

from discordbot.constants import MIN_USERS_FILTER, USER_POINTS_FILTER
from discordbot.utilities import PlaceHolderLogger
from mongo.bsepoints.points import UserPoints
from mongo.datatypes.bet import BetDB
from mongo.datatypes.revolution import RevolutionEventDB


class EmbedManager:
    """EmbedManager class.

    Generatetes messages from templates for various scenarios based on inputs.
    Centralises where we generate repeated bits of text like bet messages, revolution text, etc.
    """

    def __init__(self: "EmbedManager", logger: Logger = PlaceHolderLogger) -> None:
        """Initialisation method.

        Args:
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
        """
        self.user_points = UserPoints()
        self.logger = logger

    def get_bet_embed(
        self: "EmbedManager",
        guild: discord.Guild,
        bet: BetDB,
    ) -> discord.Embed:
        """Generates a bet embed from the given bet.

        Args:
            guild (discord.Guild): the guild Object the bet resides in
            bet (Bet): the bet dict

        Returns:
            discord.Embed: a formatted embed to send
        """
        embed = discord.Embed(colour=discord.Colour.random())

        for option in bet.option_dict:
            betters = [bet.betters[b] for b in bet.betters if bet.betters[b].emoji == option]
            if betters:
                val = ""
                for better in sorted(betters, key=lambda b: b.points, reverse=True):
                    if val:
                        val += "\n"
                    better_info = guild.get_member(better.user_id)
                    _better = self.user_points.find_user(better.user_id, guild.id) if not better_info else {}
                    val += (
                        f"**{better_info.name if better_info else (_better.name or better.user_id)}** "
                        f"(_{better.points}_)"
                    )
            else:
                val = "No-one has bet on this option yet."
            embed.add_field(name=f"{option} - {bet.option_dict[option].val}", value=val, inline=False)

        if not bet.active:
            footer = "This bet is closed for new bets. Awaiting results from the bet creator."
        elif timeout := bet.timeout:
            footer = f"This bet will stop taking bets on {timeout.strftime('%d %b %y %H:%M:%S')}."
        else:
            footer = "Unknown state."

        embed.set_footer(text=footer)
        return embed

    def get_leaderboard_embed(
        self: "EmbedManager",
        guild: discord.Guild,
        number: int | None,
        username: str | None,
    ) -> str:
        """Generates the leaderboard text.

        Args:
            guild (discord.Guild): the guild to create the leaderboard for
            number (int | None): how many users to display
            username (str | None): the person who triggered the command

        Returns:
            str: the formatted text
        """
        users = self.user_points.get_all_users_for_guild(guild.id)

        users = sorted(users, key=lambda x: x.points, reverse=True)

        number = len(users) if number is None else min(len(users), number)

        users = [user for user in users if not user.inactive]

        if len(users) > MIN_USERS_FILTER:
            # only filter out users with ten points if the server has lots of users
            users = [user for user in users if user.points != USER_POINTS_FILTER]

        message = "# BSEddies Leaderboard\n"

        for user in users[:number]:
            try:
                name = user.name or guild.get_member(user.uid).name
            except AttributeError:
                continue
            message += f"\n- **{users.index(user) + 1})**  {name}  :  {user.points}"

        message += (
            f"\n\nLast refreshed at `{datetime.datetime.now(tz=datetime.UTC).strftime('%d %b %y %H:%M')}` "
            f"by _{username}_."
        )

        return message

    def get_highscore_embed(
        self: "EmbedManager",
        guild: discord.Guild,
        number: int | None,
        username: str | None,
    ) -> str:
        """Genrates the highscore text.

        Args:
            guild (discord.Guild): the guild to create the highscores for
            number (int | None): how many users to display
            username (str | None): the user who triggered the command

        Returns:
            str: the formatted text
        """
        users = self.user_points.get_all_users_for_guild(guild.id)

        users = sorted(users, key=lambda x: x.high_score, reverse=True)

        number = len(users) if number is None else min(len(users), number)

        users = [user for user in users if not user.inactive]

        if len(users) > MIN_USERS_FILTER:
            # only filter out users with ten points if the server has lots of users
            users = [user for user in users if user.points != USER_POINTS_FILTER]

        message = "# BSEddies High Scores\n"

        for user in users[:number]:
            try:
                name = user.name or guild.get_member(user.uid).name
            except AttributeError:
                continue
            message += f"\n- **{users.index(user) + 1})**  {name}  :  {user.high_score}"

        message += (
            f"\n\nLast refreshed at `{datetime.datetime.now(tz=datetime.UTC).strftime('%d %b %y %H:%M')}` "
            f"by _{username}_."
        )

        return message

    @staticmethod
    def get_revolution_message(
        king_user: discord.User, role: discord.Role, event: RevolutionEventDB, guild: discord.Guild
    ) -> str:
        """Generates a revolution message.

        Args:
            king_user (discord.User): the user who is currently king
            role (discord.Role): the KING role
            event (RevolutionEventDB): the revolution event
            guild (discord.Guild): the guild the event is happening within

        Returns:
            str: the formatted text
        """
        revos = []
        for rev in event.revolutionaries:
            if rev_info := guild.get_member(rev):
                revos.append(rev_info.name)
            else:
                revos.append(str(rev))

        supps = []
        for sup in event.supporters:
            if sup_info := guild.get_member(sup):
                supps.append(sup_info.name)
            else:
                supps.append(str(sup))

        chance = max(min(event.chance, 95), 5)

        return (
            f"# REVOLUTION IS UPON US \n\n"
            f"@everyone - Yet again, we must try to overthrow our {role.mention}. {king_user.mention} has ruled "
            "tyranically for far too long and we are now offered a chance to take their BSEddies and knock him down "
            "a peg or two.\n\n"
            ""
            f"If you would like to OVERTHROW {role.mention} then you press the **OVERTHROW** button.\n"
            f"If you believe that {king_user.mention} hasn't done too bad a job then you can **SUPPORT** them to "
            "reduce the chances of revolution happening. If the King _loses_, then supporters will lose eddies "
            "alongside their King.\n"
            "The KING may spend 10% of their eddies using the _Save Thyself_ "
            "button to reduce revolution chance by 15%.\n"
            f"**Success rate**: `{chance}%`\n"
            f"**Revolutionaries**: `{', '.join(revos) if revos else None}`\n"
            f"**Supporters**: `{', '.join(supps) if supps else None}`\n"
            f"**Locked in KING eddies**: `{event.locked_in_eddies}`"
        )
