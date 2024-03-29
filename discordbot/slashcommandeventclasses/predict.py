"""Predict slash command."""

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.constants import CREATOR, HUMAN_MESSAGE_TYPES
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.tasks.eddiegains import BSEddiesManager


class Predict(BSEddies):
    """Class for handling `/bseddies predict` command."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client

        """
        super().__init__(client)
        self.manager = BSEddiesManager(client, [])
        self.activity_type = ActivityTypes.BSEDDIES_PREDICT
        self.help_string = "Predict your daily salary gain for today"
        self.command_name = "predict"

    async def predict(self, ctx: discord.ApplicationContext) -> None:
        """Command to allow a user to see how many eddies they might gain today.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.defer(ephemeral=True)

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_PREDICT)

        eddies_dict = self.manager.give_out_eddies(ctx.guild_id, False, 0)

        eddies = eddies_dict[ctx.author.id][0]
        breakdown = eddies_dict[ctx.author.id][1]
        tax = eddies_dict[ctx.author.id][2]

        king_id = self.user_points.get_current_king(ctx.guild_id).uid

        if king_id == ctx.author.id:
            tax_message = f"You're estimated to gain `{tax}` from tax gains."
        else:
            tax_message = f"You're estimated to be taxed `{tax}` by the KING"

        message = (
            f"You're estimated to gain `{eddies}` (after tax) today.\n"
            f"{tax_message}\n"
            f"\n"
            f"This is based on the following amount of interactivity today:"
        )

        for key in sorted(breakdown):
            message += f"\n - `{HUMAN_MESSAGE_TYPES[key]}`  :  **{breakdown[key]}**"

            if key in {"vc_joined", "vc_streaming"}:
                message += " seconds"

        if ctx.author.id != CREATOR:
            await ctx.followup.send(content=message, ephemeral=True)
            return

        message += "\n\nHere's everyone else's predicted eddies:\n"
        for user_id in eddies_dict:
            if user_id == ctx.author.id:
                continue

            value = eddies_dict[user_id][0]
            tax = eddies_dict[user_id][2]

            if value == 0:
                continue

            try:
                user = await ctx.guild.fetch_member(int(user_id))  # type: discord.Member
            except discord.NotFound:
                message += f"\n- `{user_id}` :  **{value}** (tax: _{tax}_)"
                continue

            message += f"\n- `{user_id}` {user.display_name} :  **{value}** (tax: _{tax}_)"

        await ctx.followup.send(content=message, ephemeral=True)
