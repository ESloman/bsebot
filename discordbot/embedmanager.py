"""Contains our EmbedManager class."""

import datetime

import discord
from slomanlogger import SlomanLogger

from discordbot.constants import MIN_USERS_FILTER, USER_POINTS_FILTER
from mongo.bsepoints.points import UserPoints
from mongo.datatypes.bet import BetDB
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.revolution import RevolutionEventDB
from mongo.datatypes.user import UserDB


class EmbedManager:
    """EmbedManager class.

    Generatetes messages from templates for various scenarios based on inputs.
    Centralises where we generate repeated bits of text like bet messages, revolution text, etc.
    """

    def __init__(self: "EmbedManager") -> None:
        """Initialisation method."""
        self.user_points = UserPoints()
        self.logger = SlomanLogger("bsebot")

    def _get_bet_embed_option_val(self, bet: BetDB, option: str) -> str:
        betters = [bet.betters[b] for b in bet.betters if bet.betters[b].emoji == option]
        if not betters:
            return "No-one has bet on this option yet."
        val = ""
        for better in sorted(betters, key=lambda b: b.points, reverse=True):
            if val:
                val += "\n"
            better_db = self.user_points.find_user(better.user_id, bet.guild_id)
            val += f"**{better_db.name or better.user_id}** (_{better.points}_)"
        return val

    def get_bet_embed(
        self: "EmbedManager",
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
            val = self._get_bet_embed_option_val(bet, option)
            embed.add_field(name=f"{option} - {bet.option_dict[option].val}", value=val, inline=False)

        if not bet.active:
            footer = "This bet is closed for new bets. Awaiting results from the bet creator."
        elif timeout := bet.timeout:
            footer = f"This bet will stop taking bets on {timeout.strftime("%d %b %y %H:%M:%S")}."
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
            f"\n\nLast refreshed at `{datetime.datetime.now(tz=datetime.UTC).strftime("%d %b %y %H:%M")}` "
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
            f"\n\nLast refreshed at `{datetime.datetime.now(tz=datetime.UTC).strftime("%d %b %y %H:%M")}` "
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
            f"**Revolutionaries**: `{", ".join(revos) if revos else None}`\n"
            f"**Supporters**: `{", ".join(supps) if supps else None}`\n"
            f"**Locked in KING eddies**: `{event.locked_in_eddies}`"
        )

    @staticmethod
    def get_revolution_bribe_message(guild_db: GuildDB, event: RevolutionEventDB, user: UserDB, bribe_cost: int) -> str:
        """Generates a revolution bribe message.

        Args:
            guild_db (GuildDB): the guild DB
            event (RevolutionEventDB): the revolution event
            user (UserDB): the user
            bribe_cost (int): the cost of a bribe

        Returns:
            str: the generated message
        """
        return (
            f"Hey <@{guild_db.king}>,\n"
            f"Looks like you're in a bit of trouble with that revolution in **{guild_db.name}**. "
            f"The chance is currently **{event.chance}%** "
            f"{"(capped at 95%) " if event.chance >= 95 else ""}"  # noqa: PLR2004
            "and you can't afford to save thyself to reduce that. "
            "_But_, I have an offer for you that might help if you're willing to accept it.\n\n"
            "For a small price, I will _secretly_ reduce the revolution chance by *50* for you. "
            "Here are the details:\n"
            "### What happens if you accept?\n"
            f"- revolution chance reduced by 50 (so to _{event.chance - 50}_ for you)\n"
            f"- if the chance is still above 50, chance is capped to 50 "
            f"({"won't affect you" if (event.chance - 50) > 50 else "will affect you"})\n"  # noqa: PLR2004
            f"- I will take _{bribe_cost}_ eddies off of you (leaving you on _{user.points - bribe_cost}_)\n"
            f"- once the event is over, I will let you know if accepting the bribe actually helped or not\n"
            "\n"
            "### What happens if you refuse?\n"
            "- absolutely nothing.\n"
            "\n"
            f"### Why {bribe_cost}?\n"
            f"There's currently {bribe_cost * 2} eddies between you and the next person on the leaderboard. "
            "This is half that so it keeps you in the lead. Remember to up the taxrate to keep your lead!\n"
            "\n"
            "### Will anyone find out?\n"
            "Nope! I won't change the 'publicly' viewable chance.\n"
            "\n"
            "### Are there any downsides?\n"
            "Reducing the chance doesn't guarantee a win. It's still possible you accept and still lose.\n"
            "\n"
            "### Is every King offered this chance?\n"
            "Nope! Only Kings that look like they're going to fail a revolution and have no other options "
            "(aka, not enough eddies to use 'save thyself'). This option is also only available to Kings "
            "who haven't been King for too long and Kings who aren't often King.\n"
        )
