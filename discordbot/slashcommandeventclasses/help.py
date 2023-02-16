import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses import BSEddies


class BSEddiesHelp(BSEddies):
    """
    Class for handling `/help` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def help(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic view method for handling help slash commands.

        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.HELP)

        message = (
            "**HELP**"
            "\n\n"
            "Eddies management commands\n"
            "`/view` - View _your_ eddies\n"
            "`/leaderboard` - see the eddies leaderboard\n"
            "`/highscores` - see the eddies highscore leaderboard\n"
            "`/predict` - predict how many eddies you'll get today from salary"
            "`/gift` - gift some eddies to a friend\n"
            "`/transactions` - view your eddies transactions\n"
            "\n"
            "Bet commands\n"
            "`/create` - create a new bet\n"
            "`/autogenerate` - autogenerate bets from a pool\n"
            "`/place` - place eddies on a bet\n"
            "`/close` - close a bet you created\n"
            "`/refresh` - refreshes a bet from the DB\n"
            "`/active` - returns all the active bets\n"
            "`/pending` - returns all the bets _you_ have eddies on\n"
            "\n"
            "KING commands\n"
            "`/pledge` - pledge your allegiance to a side against/for the KING\n"
            "`/rename` - pay to rename either the _KING_ role, _SUPPORTER_ role, or the _REVOLUTIONARY_ role\n"
            "`/taxrate` (KING only) - change the taxrate\n"
            "`/bless` (KING only) - bless everyone or your supporters with eddies\n"
            "\n"
            "Misc commnads\n"
            "`/help` - this command\n"
            "`/suggest` - suggest an improvement/report a bug\n"
            "`/stats` (soon) - see your Best Summer Ever statistics\n"
            "`/wrapped22` - see your Best Summer Ever wrapped\n"
            "\n\n"
            "Repo link: https://github.com/ESloman/bsebot"
        )

        await ctx.respond(content=message, ephemeral=True)
