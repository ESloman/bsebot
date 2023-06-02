
import datetime
import re

import discord
import pandas
import seaborn

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import WORDLE_SCORE_REGEX
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class WordleStatsShareView(discord.ui.View):
    def __init__(self, ):
        super().__init__(timeout=None)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.blurple, row=2, disabled=False)
    async def submit_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        # add username
        content = interaction.message.content.replace(
            "Your Wordle Stats",
            f"{interaction.user.display_name}'s Wordle Stats"
        )

        _files = [
            await attachment.to_file() for attachment in
            interaction.message.attachments
        ]

        await interaction.channel.send(
            content=content,
            silent=True,
            suppress=True,
            files=_files
        )
        try:
            await interaction.response.edit_message(content="Shared.", view=None, delete_after=2)
        except discord.NotFound:
            pass


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

        msg = "# Your Wordle Stats\n\n"
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

        msg += "\n## Annually\n"
        now = datetime.datetime.now()
        # calculate averages for all years and months
        all_month_avgs = {}
        for year in range(2022, now.year + 1):  # need to add one as end is exlusive
            # we only started doing it in 2022
            year_start = now.replace(year=year, day=1, month=1, hour=0, minute=0, second=1)
            year_end = year_start.replace(year=year_start.year + 1)
            wordles_this_year = [wordle for wordle in all_wordles if year_start < wordle["timestamp"] < year_end]
            scores_this_year = [wordle["guesses"] for wordle in wordles_this_year if wordle["guesses"] != 7]
            try:
                avg_this_year = round(sum(scores_this_year) / len(scores_this_year), 2)
            except ZeroDivisionError:
                avg_this_year = 0.0
            msg += f"- Your *{year_start.year}* average is `{avg_this_year}`.\n"

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

                wordles_this_month = [wordle for wordle in all_wordles if month_start < wordle["timestamp"] < month_end]
                scores_this_month = [wordle["guesses"] for wordle in wordles_this_month if wordle["guesses"] != 7]
                try:
                    avg_this_month = round(sum(scores_this_month) / len(scores_this_month), 2)
                except ZeroDivisionError:
                    # user didn't do any this month
                    avg_this_month = 0.0
                all_month_avgs[month_start] = avg_this_month

        msg += "\n## Monthly\n"
        for month in range(1, now.month):  # don't add one as we don't care about current month
            month_start = now.replace(day=1, month=month, hour=0, minute=0, second=1)
            avg_this_month = all_month_avgs[month_start]
            msg += f"- Your *{month_start.strftime('%b %y')}* average is `{avg_this_month}`.\n"

        # calculate average for this month
        month_start = now.replace(day=1, hour=0, minute=0, second=1)
        month_end = month_start + datetime.timedelta(days=31)  # month end is any day beyond today
        wordles_this_month = [wordle for wordle in all_wordles if month_start < wordle["timestamp"] < month_end]
        scores_this_month = [wordle["guesses"] for wordle in wordles_this_month if wordle["guesses"] != 7]
        try:
            avg_this_month = round(sum(scores_this_month) / len(scores_this_month), 2)
        except ZeroDivisionError:
            avg_this_month = 0.0

        msg += f"- Your average this month so far is `{avg_this_month}`.\n"

        top_month = sorted(
            [a for a in all_month_avgs if all_month_avgs[a]],
            key=lambda x: all_month_avgs[x],
            reverse=False
        )[0]
        msg += f"\n- Your **best** ever month was {top_month.strftime('%b %y')} with `{all_month_avgs[top_month]}`\n"

        msg += "\n## Lifetime Score count\n"

        guesses = {x: 0 for x in range(1, 8)}
        for wordle in all_wordles:
            guesses[wordle["guesses"]] += 1

        for x in range(1, 7):
            msg += f"- **{x}**: `{guesses[x]}`\n"
        msg += f"- **X**: `{guesses[7]}`\n"

        msg += "\n\nBelow is a graph of your monthly average over time."

        # create figure
        dates_data = [(key.strftime("%b %y"), all_month_avgs[key], total_avg) for key in all_month_avgs]
        df = pandas.DataFrame(data=dates_data, columns=["month", "average score", "lifetime avg"])
        seaborn.set_theme()
        plot = seaborn.lineplot(df, x="month", y="average score")
        plot.figure.autofmt_xdate()
        plot.set_title(f"{ctx.user.display_name}'s Monthly Wordle Averages")
        plot.plot(
            [d[0] for d in dates_data],
            [total_avg]*len(dates_data),
            label="Lifetime average",
            linestyle="--",
            color="red"
        )
        plot.figure.savefig(f"{ctx.user.id}.png")
        graph = discord.File(f"{ctx.user.id}.png")

        view = WordleStatsShareView()
        await ctx.followup.send(content=msg, view=view, ephemeral=True, files=[graph])
