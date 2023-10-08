
import discord
from discord import Interaction
from discord.ui import Select


class BSEddiesChannelSelect(Select):
    def __init__(self):
        super().__init__(
            discord.ComponentType.channel_select,
            placeholder="Select channel for BSEddies stuff",
            channel_types=[
                discord.ChannelType.text, discord.ChannelType.private
            ],
            min_values=0,
            max_values=1,
            disabled=False
        )

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        try:
            selected = interaction.data["values"][0]
        except (IndexError, AttributeError):
            # nothing selected
            selected = None

        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)


class BSEddiesRoleSelect(Select):
    def __init__(self, role_type: str = "KING"):
        super().__init__(
            discord.ComponentType.role_select,
            placeholder=f"Select role for the {role_type}",
            min_values=0,
            max_values=1,
            disabled=False
        )

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        try:
            selected = interaction.data["values"][0]
        except (IndexError, AttributeError):
            # nothing selected
            selected = None

        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)
