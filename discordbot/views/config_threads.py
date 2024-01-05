"""Thread config views."""

import discord

from discordbot.selects.threadconfig import ThreadActiveSelect, ThreadConfigSelect, ThreadDaySelect
from mongo.bsedataclasses import SpoilerThreads
from mongo.datatypes import ThreadDB


class ThreadConfigView(discord.ui.View):
    """Class for thread config view."""

    def __init__(self, threads: list[ThreadDB]) -> None:
        """Initialisation method.

        Args:
            threads (list[Thread]): list of threads
        """
        super().__init__(timeout=120)

        self.spoiler_threads = SpoilerThreads()

        threads = [t for t in threads if t.active]
        self.threads = threads
        self.thread_select = ThreadConfigSelect(threads)
        self.add_item(self.thread_select)

        self.active_select = ThreadActiveSelect()
        self.add_item(self.active_select)

        self.day_select = ThreadDaySelect()
        self.add_item(self.day_select)

    async def update(self) -> None:
        """View update method.

        Can be called by child types when something changes.
        """
        # updates all the selects with new values
        selected_thread = next(t for t in self.threads if str(t.thread_id) == self.thread_select._selected_values[0])  # noqa: SLF001

        for opt in self.day_select.options:
            opt.default = False

        if selected_thread.day:
            for opt in self.day_select.options:
                if int(opt.value) == selected_thread.day:
                    opt.default = True
                    break

        self.active_select.disabled = False
        self.day_select.disabled = False

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        selected_thread = next(t for t in self.threads if str(t.thread_id) == self.thread_select._selected_values[0])  # noqa: SLF001

        try:
            day = int(self.day_select._selected_values[0])  # noqa: SLF001
        except (IndexError, AttributeError, TypeError):
            # look for default as user didn't select one explicitly
            for opt in self.day_select.options:
                if opt.default:
                    day = int(opt.value)
                    break

        if day == 7:  # noqa: PLR2004
            # 7 is for when user doesn't want a day set
            day = None

        try:
            active = bool(int(self.active_select._selected_values[0]))  # noqa: SLF001
        except (IndexError, AttributeError, TypeError):
            # user didn't select a value
            # true is default here
            active = True

        self.spoiler_threads.update({"_id": selected_thread._id}, {"$set": {"active": active, "day": day}})  # noqa: SLF001

        await interaction.response.edit_message(content="Thread updated.", view=None, delete_after=10)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
