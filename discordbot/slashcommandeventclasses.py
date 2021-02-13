import discord
import discord_slash

from discordbot.clienteventclasses import BaseEvent
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserBets, UserPoints


class BSEEddies(BaseEvent):
    def __init__(self, guilds, beta_mode=False):
        super().__init__(guilds, beta_mode=beta_mode)

    async def _handle_validation(self, ctx: discord_slash.model.SlashContext, **kwargs):
        """
        Internal method for validating slash command inputs.
        :param ctx:
        :return:
        """
        if ctx.guild.id not in self.guild_ids:
            return False

        if self.beta_mode and ctx.channel.id != 809773876078575636:
            msg = f"These features are in BETA mode and this isn't a BETA channel."
            await ctx.send(content=msg, hidden=True)
            return False

        return True


class BSEddiesView(BSEEddies):
    def __init__(self, guilds, beta_mode=False):
        super().__init__(guilds, beta_mode=beta_mode)

    async def view(self, ctx: discord_slash.model.SlashContext):
        """
        Basic view method for handling view slash commands.
        If validation passes - it will inform the user of their current Eddies total.
        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        points = self.user_points.get_user_points(ctx.author.id, ctx.guild.id)
        msg = f"You have **{points}** :money_with_wings:`BSEDDIES`:money_with_wings:!"
        await ctx.send(content=msg, hidden=True)


class BSEddiesLeaderboard(BSEEddies):
    def __init__(self, guilds, beta_mode=False):
        super().__init__(guilds, beta_mode=beta_mode)

    async def leaderboard(self, ctx: discord_slash.model.SlashContext):
        if not await self._handle_validation(ctx):
            return

        embed = self.embed_manager.get_leaderboard_embed(ctx.guild, 5)
        message = await ctx.channel.send(content=embed)
        await message.add_reaction(u"▶️")
