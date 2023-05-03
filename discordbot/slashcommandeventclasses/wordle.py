
import datetime
import re

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import WORDLE_SCORE_REGEX
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class Wordle(BSEddies):
    """
    Class for handling `/wordle` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.activity_type = ActivityTypes.WORDLE
        self.help_string = "View some wordle stats"
        self.command_name = "wordle"

    async def wordle(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic view method for handling wordle slash commands.

        Sends an ephemeral message to the user with their total eddies and any "pending" eddies they
        have tied up in bets.

        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.response.defer(ephemeral=True)

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.WORDLE)

        user_id = ctx.user.id

        all_wordles = self.interactions.query(
            {
                "message_type": "wordle",
                "user_id": user_id,
                "guild_id": ctx.guild.id
            }
        )

        failed_wordles = [wordle for wordle in all_wordles if "X/6" in wordle["content"]]
        failed_perc = round((len(failed_wordles) / len(all_wordles)) * 100, 2)

        msg = "**Your Wordle Stats**\n\n"
        msg += f"- You have attempted `{len(all_wordles)}` and posted them to this server.\n"
        msg += f"- You have failed **{len(failed_wordles)}** (`{failed_perc}%`) of them.\n"

        for wordle in all_wordles:
            result = re.search(WORDLE_SCORE_REGEX, wordle["content"]).group()
            guesses = result.split("/")[0]

            if guesses == "X":
                guesses = 7
            else:
                guesses = int(guesses)
            wordle["guesses"] = guesses

        scores = [wordle["guesses"] for wordle in all_wordles if wordle["guesses"] != 7]
        total_avg = round(sum(scores) / len(scores), 2)

        msg += f"- Your *lifetime* average is `{total_avg}`.\n"

        now = datetime.datetime.now()
        # calculate averages for all years
        for year in range(2022, now.year + 1):  # need to add one as end is exlusive
            # we only started doing it in 2022
            year_start = now.replace(year=year, day=1, month=1, hour=0, minute=0, second=1)
            year_end = year_start.replace(year=year_start.year + 1)
            wordles_this_year = [wordle for wordle in all_wordles if year_start < wordle["timestamp"] < year_end]
            scores_this_year = [wordle["guesses"] for wordle in wordles_this_year if wordle["guesses"] != 7]
            avg_this_year = round(sum(scores_this_year) / len(scores_this_year), 2)
            msg += f"- Your *{year_start.year}* average is `{avg_this_year}`.\n"

        # calculate average for this month
        month_start = now.replace(day=1, hour=0, minute=0, second=1)
        month_end = month_start + datetime.timedelta(days=31)  # month end is any day beyond today
        wordles_this_month = [wordle for wordle in all_wordles if month_start < wordle["timestamp"] < month_end]
        scores_this_month = [wordle["guesses"] for wordle in wordles_this_month if wordle["guesses"] != 7]
        avg_this_month = round(sum(scores_this_month) / len(scores_this_month), 2)

        msg += f"- Your average this month so far is `{avg_this_month}`.\n"

        await ctx.followup.send(content=msg, ephemeral=True)
