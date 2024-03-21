"""Revolution views."""

from logging import Logger

import discord

from discordbot.bot_enums import TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.views.bseview import BSEView
from mongo.bsepoints.points import UserPoints
from mongo.bseticketedevents import RevolutionEvent
from mongo.datatypes.revolution import RevolutionEventDB

GIF_LINK = (
    "https://media.giphy.com/media/"
    "v1.Y2lkPTc5MGI3NjExMThwZmxrcnNvMnF5dnhrNW8zbHltNnRsemc3aT"
    "Q1Z3F1azN5OHVoMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tZCkL6BsL2AAo/giphy.gif"
)


class RevolutionBribeView(BSEView):
    """Class for revolution bribe view."""

    def __init__(self, client: BSEBot, event: RevolutionEventDB, bribe_cost: int, logger: Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the BSEBot client
            event (RevolutionEventType): the revolution event
            bribe_cost (int): the cost of the bribe
            logger (Logger): the logger to use
        """
        super().__init__(timeout=1800)
        self.client = client
        self.guild_id = event.guild_id
        self.event_id = event.event_id
        self.bribe_cost: int = bribe_cost
        self.revolutions = RevolutionEvent()
        self.user_points = UserPoints()
        self.logger = logger

    @discord.ui.button(label="Accept Offer", style=discord.ButtonStyle.green, emoji="👑")
    async def accept_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Callback for accepting the offer.

        Effectively just sets the database flag and sends a gif.

        Args:
            button (discord.ui.Button): the button being pressed
            interaction (discord.Interaction): the interaction context
        """
        self.revolutions.set_bribe_accepted_flag(self.event_id, True)
        self.user_points.increment_points(
            interaction.user.id, self.guild_id, -self.bribe_cost, TransactionTypes.REVOLUTION_BRIBE
        )
        await interaction.message.edit(content="_Offer accepted._", view=None, delete_after=5)
        await interaction.response.send_message(content=GIF_LINK)

    @discord.ui.button(label="Refuse Offer", style=discord.ButtonStyle.red, emoji="👑")
    async def refuse_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Callback for refusing the offer.

        Effectively just sets the database flag and sends a gif.

        Args:
            button (discord.ui.Button): the button being pressed
            interaction (discord.Interaction): the interaction context
        """
        self.revolutions.set_bribe_accepted_flag(self.event_id, False)
        await interaction.message.edit(content="_Offer refused._", view=None, delete_after=5)
        await interaction.response.send_message(content=GIF_LINK)
