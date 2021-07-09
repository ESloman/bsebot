import datetime
from typing import Union

import discord
import inflect

from discordbot.constants import BSEDDIES_KING_ROLES
from mongo.bsepoints import UserPoints


class EmbedManager(object):
    def __init__(self, logger):
        self.user_points = UserPoints()
        self.inflect_engine = inflect.engine()
        self.logger = logger

    @staticmethod
    def get_bet_embed(guild: discord.Guild, bet_id, bet: dict):
        """
        Gets the bet embed and returns that
        :param guild:
        :param bet_id:
        :param bet:
        :return:
        """
        embed = discord.Embed(
            description=f"**{bet['title']}**\n\nBet ID: {bet_id}",
            color=discord.Color.blue(),
        )

        for option in bet["option_dict"]:
            betters = [bet['betters'][b] for b in bet['betters'] if bet['betters'][b]["emoji"] == option]
            if betters:
                val = ""
                for better in sorted(betters, key=lambda b: b["points"], reverse=True):
                    if val:
                        val += "\n"
                    better_info = guild.get_member(better["user_id"])
                    val += f"- {better_info.name} - {better['points']}"
            else:
                val = "No-one has bet on this option yet."
            embed.add_field(
                name=f"{option} - {bet['option_dict'][option]['val']}",
                value=val,
                inline=False
            )

        if not bet["active"]:
            footer = "This bet is closed for new bets. Awaiting results from the bet creator."
        elif timeout := bet.get("timeout"):
            footer = f"This bet will stop taking bets on {timeout.strftime('%d %b %y %H:%M:%S')} "
        else:
            footer = None

        if footer is not None:
            embed.set_footer(text=footer)

        return embed

    def get_leaderboard_embed(self, guild: discord.Guild, number: Union[int, None]):
        """
        Return a str that will be the leaderboard table
        :param guild:
        :param number:
        :return:
        """
        users = self.user_points.get_all_users_for_guild(guild.id)

        users = sorted(users, key=lambda x: x["points"], reverse=True)

        if number is None:
            number = len(users)
        else:
            number = number if number < len(users) else len(users)

        message = (
            "**BSEddies Leaderboard**\n"
            f"Leaderboard is correct as of: "
            f"{datetime.datetime.now().strftime('%d %b %y %H:%M:%S')}\n"
        )

        for user in users[:number]:
            try:
                name = guild.get_member(user["uid"]).name
            except AttributeError:
                continue
            message += f"\n**{users.index(user) + 1})**  {name}  :  {user['points']}"

        if number < 6:
            message += "\n\n :arrow_forward: for longer list"

        return message

    def get_highscore_embed(self, guild: discord.Guild, number: Union[int, None]):
        """
        Return a str that will be the leaderboard table
        :param guild:
        :param number:
        :return:
        """
        users = self.user_points.get_all_users_for_guild(guild.id)

        users = sorted(users, key=lambda x: x.get("high_score", 0), reverse=True)

        if number is None:
            number = len(users)
        else:
            number = number if number < len(users) else len(users)

        message = (
            "**BSEddies High Scores**\n"
            f"This is correct as of: "
            f"{datetime.datetime.now().strftime('%d %b %y %H:%M:%S')}\n"
        )

        for user in users[:number]:
            try:
                name = guild.get_member(user["uid"]).name
            except AttributeError:
                continue
            message += f"\n**{users.index(user) + 1})**  {name}  :  {user.get('high_score', 0)}"

        if number < 6:
            message += "\n\n :arrow_forward: for longer list"

        return message

    @staticmethod
    def get_revolution_message(king_user: discord.User, role: discord.Role, event: dict):
        """
        Method for creating a 'Revolution' message

        :param king_user:
        :param role:
        :param event:
        :return:
        """

        message = (
            f"**REVOLUTION IS UPON US**\n\n"
            f"@everyone - Yet again, we must try to overthrow our {role.mention}. {king_user.mention} has ruled "
            f"tyranically for far too long and we are now offered a chance to take their BSEddies and knock him down "
            f"a peg or two.\n\n"
            f""
            f"To do so, we must do it in an orderly fashion. If you would like to participate, please buy a ticket "
            f"(by reacting appropriately). Each ticket bought will increase our success rate. "
            f"_**If we are successful**_, the {role.mention}, will have their BSEddies cut in half. The amount of "
            f"eddies that KING will lose is locked in from this moment onwards. These eddies will be re-distributed "
            f"amongst those who bought tickets. **_If we fail_**, then the eddies spent on buying tickets will be "
            f"given to {role.mention}.\n\n"
            f"**Event ID**: `{event['event_id']}`\n"
            f"**Tickets bought**: `{len(event['ticket_buyers'])}`\n"
            f"**Success rate**: `{event['chance']}%`\n"
            f"**Ticket price**: `{event['ticket_cost']}`\n"
            f"**Locked in KING eddies**: `{event.get('locked_in_eddies')}`\n"
            f"**Event time**: `{event['expired'].strftime('%d %b %y %H:%M:%S')}`"
        )

        return message
