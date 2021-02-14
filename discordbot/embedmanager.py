import datetime
from typing import List, Union, Dict

import discord
import inflect
from prettytable import PrettyTable

from mongo.bsepoints import UserPoints


class EmbedManager(object):
    def __init__(self):
        self.user_points = UserPoints()
        self.inflect_engine = inflect.engine()
        self.pretty_table = PrettyTable()

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
            title=bet["title"],
            description=f"Bet ID: {bet_id}",
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

        self.pretty_table = PrettyTable()

        self.pretty_table.field_names = [" Position ", " Name ", " BSEDDIES "]

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
            name = guild.get_member(user["uid"]).name
            self.pretty_table.add_row(
                [users.index(user) + 1, name, user["points"]]
            )
            message += f"\n**{users.index(user) + 1})**  {name}  :  {user['points']}"

        # message += self.pretty_table.get_string()

        if number < 6:
            message += "\n\n :arrow_forward: for longer list"

        return message
