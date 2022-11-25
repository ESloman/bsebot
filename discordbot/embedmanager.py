import datetime
from typing import Optional, Union

import discord

from mongo.bsepoints import UserPoints


class EmbedManager(object):
    def __init__(self, logger):
        self.user_points = UserPoints()
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
                    val += f"- {better_info.name if better_info else better['user_id']} - {better['points']}"
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

    def get_leaderboard_embed(self, guild: discord.Guild, number: Union[int, None], username: Optional[str]):
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

        users = [user for user in users if user["points"] != 10 and not user.get("inactive")]

        message = (
            "**BSEddies Leaderboard**\n"
        )

        for user in users[:number]:
            try:
                name = guild.get_member(user["uid"]).name
            except AttributeError:
                continue
            message += f"\n**{users.index(user) + 1})**  {name}  :  {user['points']}"

        message += (
            f"\n\nLast refreshed at `{datetime.datetime.now().strftime('%d %b %y %H:%M:%S')}` by _{username}_."
        )

        return message

    def get_highscore_embed(self, guild: discord.Guild, number: Union[int, None], username: Optional[str]):
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

        users = [user for user in users if user["points"] != 10 and not user.get("inactive")]

        message = (
            "**BSEddies High Scores**\n"
        )

        for user in users[:number]:
            try:
                name = guild.get_member(user["uid"]).name
            except AttributeError:
                continue
            message += f"\n**{users.index(user) + 1})**  {name}  :  {user.get('high_score', 0)}"

        message += (
            f"\n\nLast refreshed at `{datetime.datetime.now().strftime('%d %b %y %H:%M:%S')}` by _{username}_."
        )

        return message

    @staticmethod
    def get_revolution_message(king_user: discord.User, role: discord.Role, event: dict, guild: discord.Guild):
        """
        Method for creating a 'Revolution' message

        :param king_user:
        :param role:
        :param event:
        :return:
        """
        revos = []
        for rev in event.get('revolutionaries', []):
            if rev_info := guild.get_member(rev):
                revos.append(rev_info.name)
            else:
                revos.append(rev)

        supps = []
        for sup in event.get('supporters', []):
            if sup_info := guild.get_member(sup):
                supps.append(sup_info.name)
            else:
                supps.append(sup)

        message = (
            f"**REVOLUTION IS UPON US**\n\n"
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
            f"**Event ID**: `{event['event_id']}`\n"
            f"**Success rate**: `{max(min(event['chance'], 100), 0)}%`\n"
            f"**Revolutionaries**: `{', '.join(revos) if revos else None}`\n"
            f"**Supporters**: `{', '.join(supps) if supps else None}`\n"
            f"**Locked in KING eddies**: `{event.get('locked_in_eddies')}`\n"
            f"**Event time**: `{event['expired'].strftime('%d %b %y %H:%M:%S')}`"
        )

        return message
