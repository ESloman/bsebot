from typing import List, Union, Dict

import discord
import inflect

from mongo.bsepoints import UserPoints


class EmbedManager(object):
    def __init__(self):
        self.user_points = UserPoints()
        self.inflect_engine = inflect.engine()

    @staticmethod
    def get_bet_embed(guild: discord.Guild, bet_id, bet: dict):
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
        return embed

    def get_leaderboard_embed(self, guild: discord.Guild, number: Union[int, None]):
        users = self.user_points.get_all_users_for_guild(guild.id)

        users = sorted(users, key=lambda x: x["points"], reverse=True)

        embed = discord.Embed(
            title="BSEddies Leaderboard",
            color=discord.Color.green(),
            description=""
        )

        message = ""

        if number is None:
            number = len(users)
        else:
            number = number if number < len(users) else len(users)

        for user in users[:number]:
            name = guild.get_member(user["uid"]).name
            con = f":{self.inflect_engine.number_to_words(users.index(user) + 1)}: {name}  :  {user['points']}"
            if message:
                message += "\n"
            message += con

        if number < 6:
            message += "\n\n :arrow_forward: for longer list"

        embed.description = message

        return embed
