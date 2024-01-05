"""BSEddies slash command base class."""

import logging
from typing import TYPE_CHECKING

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.constants import CREATOR

if TYPE_CHECKING:
    from discordbot.bot_enums import ActivityTypes


class BSEddies(BaseEvent):
    """A base BSEddies event for any shared methods across.

    All slash command classes will inherit from this class.
    """

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.dmable = False

        # these need to be set
        self.activity_type: ActivityTypes | None = None
        self.help_string: str | None = None
        self.command_name: str | None = None

    async def _handle_validation(
        self, ctx: discord.ApplicationContext | discord.Interaction, **kwargs: dict[str, any]
    ) -> bool:
        """Internal method for validating slash command inputs.

        Args:
            ctx (discord.ApplicationContext | discord.Interaction): the context

        Returns:
            bool: whether we pass validation or not
        """
        response = ctx.respond if type(ctx) is discord.ApplicationContext else ctx.response.send_message

        if not ctx.guild and not self.dmable:
            msg = "This command doesn't work in DMs (yet)."
            await response(content=msg)
            return False

        if kwargs.get("admin") and ctx.user.id != CREATOR:
            msg = "You do not have the permissions to use this command."
            await response(content=msg, ephemeral=True, delete_after=10)
            return False

        if "friend" in kwargs and (isinstance(kwargs["friend"], discord.Member | discord.User)):
            if kwargs["friend"].bot:
                msg = "Bots cannot be gifted eddies."
                await response(content=msg, ephemeral=True, delete_after=10)
                return False

            if kwargs["friend"].id == ctx.user.id:
                msg = "You can't gift yourself points."
                await response(content=msg, ephemeral=True, delete_after=10)
                return False

        if "amount" in kwargs and isinstance(kwargs["amount"], int) and kwargs["amount"] < 0:
            msg = 'You can\'t _"gift"_ someone negative points.'
            await response(content=msg, ephemeral=True, delete_after=10)
            return False

        return True
