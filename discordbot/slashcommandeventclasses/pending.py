
import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class Pending(BSEddies):
    """
    Class for handling `/bseddies pending` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.activity_type = ActivityTypes.BSEDDIES_PENDING
        self.help_string = "See all the pending bets you have eddies on"
        self.command_name = "pending"

    async def pending(self, ctx: discord.ApplicationContext) -> None:
        """
        Simple method for listing all the pending bets for the user that executed this command

        A 'pending' bet is a bet that hasn't been closed or resolved the the user has invested eddies in to

        This will send an ephemeral message to the user with all their pending bets.

        :param ctx: slash command context
        :return: None
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_PENDING)

        bets = self.user_bets.get_all_pending_bets_for_user(ctx.author.id, ctx.guild.id)

        message = "Here are all your pending bets:\n"

        for bet in bets:
            if "channel_id" not in bet or "message_id" not in bet:
                continue

            link = f"https://discordapp.com/channels/{ctx.guild.id}/{bet['channel_id']}/{bet['message_id']}"

            add_text = "OPEN FOR NEW BETS" if bet.get("active") else "CLOSED - AWAITING RESULT"

            pt = (f"**{bets.index(bet) + 1})** [{bet['bet_id']} - `{add_text}`] _{bet['title']}_"
                  f"\nOutcome: {bet['betters'][str(ctx.author.id)]['emoji']}\n"
                  f"Points: **{bet['betters'][str(ctx.author.id)]['points']}**\n{link}\n\n")
            message += pt

            if (len(message) + 400) > 2000 and bet != bets[-1]:
                await ctx.respond(content=message, ephemeral=True)
                message = ""

        if len(bets) == 0:
            message = "You have no pending bets :("

        await ctx.respond(content=message, ephemeral=True)
