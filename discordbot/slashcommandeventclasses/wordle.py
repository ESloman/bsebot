"""Wordle slash command."""

import contextlib
import datetime
import logging
import re
from dataclasses import asdict

import discord
import pytz
import seaborn as sns

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.constants import WORDLE_SCORE_REGEX
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from mongo.datatypes.message import MessageDB, WordleMessageDB


class WordleStatsShareView(discord.ui.View):
    """Wordle stats share view."""

    def __init__(
        self,
    ) -> None:
        """Initialisation method."""
        super().__init__(timeout=None)

    @staticmethod
    @discord.ui.button(label="Share", style=discord.ButtonStyle.blurple, row=2, disabled=False)
    async def submit_button_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): _description_
            interaction (discord.Interaction): _description_
        """
        # add username
        content = interaction.message.content.replace(
            "Your Wordle Stats",
            f"{interaction.user.display_name}'s Wordle Stats",
        )

        _files = [await attachment.to_file() for attachment in interaction.message.attachments]

        await interaction.channel.send(content=content, silent=True, suppress=True, files=_files)
        with contextlib.suppress(discord.NotFound):
            await interaction.response.edit_message(content="Shared.", view=None, delete_after=2)


class Wordle(BSEddies):
    """Class for handling `/wordle` commands."""

    def __init__(self, client: BSEBot, guild_ids: list[int], logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.activity_type = ActivityTypes.WORDLE
        self.help_string = "View some wordle stats"
        self.command_name = "wordle"

    @staticmethod
    def _add_guesses(wordles: list[MessageDB]) -> list[WordleMessageDB]:
        """Adds the 'guesses' key to a list of wordle interactions.

        Args:
            _wordles (list[dict]): the list of wordle messages
        """
        _wordles = []
        for wordle in wordles:
            result = re.search(WORDLE_SCORE_REGEX, wordle.content).group()
            guesses = result.split("/")[0]

            guesses = 7 if guesses == "X" else int(guesses)
            _wordles.append(WordleMessageDB(**asdict(wordle), guesses=guesses))
        return _wordles

    @staticmethod
    def _calculate_averages(wordles: list[WordleMessageDB]) -> tuple[dict[int, float], dict[datetime.datetime, float]]:
        now = datetime.datetime.now(tz=pytz.utc)
        # calculate averages for all years and months
        monthly_avgs = {}
        yearly_avgs = {}
        for year in range(2022, now.year + 1):  # need to add one as end is exlusive
            # we only started doing it in 2022
            year_start = now.replace(year=year, day=1, month=1, hour=0, minute=0, second=1, microsecond=0)
            year_end = year_start.replace(year=year_start.year + 1)
            wordles_this_year = [wordle for wordle in wordles if year_start < wordle.timestamp < year_end]
            scores_this_year = [wordle.guesses for wordle in wordles_this_year if wordle.guesses != 7]  # noqa: PLR2004

            try:
                avg_this_year = round(sum(scores_this_year) / len(scores_this_year), 2)
            except ZeroDivisionError:
                avg_this_year = 0.0

            yearly_avgs[year_start.year] = avg_this_year

            # calculate stats for each month in this year
            for month in range(1, 13):
                month_start = year_start.replace(day=1, month=month, hour=0, minute=0, second=1)

                if month_start.year == now.year and month_start.month > now.month:
                    # unnecessary data
                    continue

                try:
                    month_end = month_start.replace(month=month_start.month + 1)
                except ValueError:
                    # can't have 13 months
                    month_end = month_start.replace(year=month_start.year + 1, month=1)

                wordles_this_month = [wordle for wordle in wordles if month_start < wordle.timestamp < month_end]
                scores_this_month = [
                    wordle.guesses
                    for wordle in wordles_this_month
                    if wordle.guesses != 7  # noqa: PLR2004
                ]

                try:
                    avg_this_month = round(sum(scores_this_month) / len(scores_this_month), 2)
                except ZeroDivisionError:
                    # user didn't do any this month
                    avg_this_month = 0.0

                monthly_avgs[month_start] = avg_this_month

        return yearly_avgs, monthly_avgs

    async def wordle(self, ctx: discord.ApplicationContext) -> None:  # noqa: PLR0915
        """Basic view method for handling wordle slash commands.

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

        _all_wordles = self.interactions.query({"message_type": "wordle", "guild_id": ctx.guild.id}, limit=100000)

        all_wordles = [wordle for wordle in _all_wordles if wordle.user_id == user_id]
        bot_wordles = [wordle for wordle in _all_wordles if wordle.user_id == self.client.user.id]
        server_wordles = [wordle for wordle in _all_wordles if wordle.user_id != self.client.user.id]

        failed_wordles = [wordle for wordle in all_wordles if "X/6" in wordle.content]
        failed_perc = round((len(failed_wordles) / len(all_wordles)) * 100, 2)

        msg = "# Your Wordle Stats\n\n"
        msg += f"- You have attempted `{len(all_wordles)}` and posted them to this server.\n"
        msg += f"- You have failed **{len(failed_wordles)}** (`{failed_perc}%`) of them.\n"

        all_wordles = self._add_guesses(all_wordles)
        bot_wordles = self._add_guesses(bot_wordles)
        server_wordles = self._add_guesses(server_wordles)

        scores = [wordle.guesses for wordle in all_wordles if wordle.guesses != 7]  # noqa: PLR2004
        total_avg = round(sum(scores) / len(scores), 2)

        msg += f"- Your *lifetime* average is `{total_avg}`.\n"

        msg += "\n## Annually\n"
        our_year_avgs, all_month_avgs = self._calculate_averages(all_wordles)

        for year in our_year_avgs:
            msg += f"- Your *{year}* average is `{our_year_avgs[year]}`.\n"

        _, bot_month_avgs = self._calculate_averages(bot_wordles)
        _, server_month_avgs = self._calculate_averages(server_wordles)

        now = datetime.datetime.now(tz=pytz.utc)

        msg += "\n## Monthly\n"
        for month in range(1, now.month):  # don't add one as we don't care about current month
            month_start = now.replace(day=1, month=month, hour=0, minute=0, second=1, microsecond=0)
            avg_this_month = all_month_avgs[month_start]
            msg += f"- Your *{month_start.strftime('%b %y')}* average is `{avg_this_month}`.\n"

        # calculate average for this month
        month_start = now.replace(day=1, hour=0, minute=0, second=1)
        month_end = month_start + datetime.timedelta(days=31)  # month end is any day beyond today
        wordles_this_month = [wordle for wordle in all_wordles if month_start < wordle.timestamp < month_end]
        scores_this_month = [wordle.guesses for wordle in wordles_this_month if wordle.guesses != 7]  # noqa: PLR2004
        try:
            avg_this_month = round(sum(scores_this_month) / len(scores_this_month), 2)
        except ZeroDivisionError:
            avg_this_month = 0.0

        msg += f"- Your average this month so far is `{avg_this_month}`.\n"

        top_month = sorted(
            [a for a in all_month_avgs if all_month_avgs[a]],
            key=lambda x: all_month_avgs[x],
            reverse=False,
        )[0]
        msg += f"\n- Your **best** ever month was {top_month.strftime('%b %y')} with `{all_month_avgs[top_month]}`\n"

        msg += "\n## Lifetime Score count\n"

        guesses = dict.fromkeys(range(1, 8), 0)
        for wordle in all_wordles:
            guesses[wordle.guesses] += 1

        for x in range(1, 7):
            msg += f"- **{x}**: `{guesses[x]}`\n"
        msg += f"- **X**: `{guesses[7]}`\n"

        msg += "\n\nBelow is a graph of your monthly average over time."

        # create figure
        dates_data = [
            (key.strftime("%b %y"), all_month_avgs[key], total_avg)
            for key in all_month_avgs
            if key > (now - datetime.timedelta(weeks=56))
        ]
        bot_dates_data = [
            (key.strftime("%b %y"), bot_month_avgs[key], total_avg)
            for key in bot_month_avgs
            if bot_month_avgs[key] > 0 and key > (now - datetime.timedelta(weeks=56))
        ]
        server_dates_data = [
            (key.strftime("%b %y"), server_month_avgs[key], total_avg)
            for key in server_month_avgs
            if key > (now - datetime.timedelta(weeks=56))
        ]

        sns.set_theme()
        plot = sns.lineplot()

        plot.plot(
            [d[0] for d in dates_data],
            [d[1] for d in dates_data],
            label=f"{ctx.user.display_name}'s Average Score",
        )

        plot.figure.autofmt_xdate()

        plot.plot(
            [d[0] for d in dates_data],
            [total_avg] * len(dates_data),
            label=f"{ctx.user.display_name}'s lifetime average",
            linestyle="--",
        )

        plot.plot(
            [d[0] for d in bot_dates_data],
            [d[1] for d in bot_dates_data],
            label="BSEBot's Average Score",
            linestyle="--",
        )

        plot.plot(
            [d[0] for d in server_dates_data],
            [d[1] for d in server_dates_data],
            label="The Server's Average Score",
            linestyle="--",
        )

        plot.figure.legend()

        plot.figure.savefig(f"{ctx.user.id}.png")
        graph = discord.File(f"{ctx.user.id}.png")

        view = WordleStatsShareView()
        await ctx.followup.send(content=msg, view=view, ephemeral=True, files=[graph])
