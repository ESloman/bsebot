"""Thread config views."""

import discord

from discordbot.selects.threadconfig import ThreadActiveSelect, ThreadConfigSelect, ThreadDaySelect
from discordbot.views.bseview import BSEView
from mongo.bsedataclasses import SpoilerThreads
from mongo.datatypes.thread import ThreadDB


class ThreadConfigView(BSEView):
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

    async def update(self, _: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            _ (discord.Interaction): the interaction. Not used here.
        """
        # updates all the selects with new values
        selected_thread = next(
            t
            for t in self.threads
            if str(t.thread_id) == self.thread_select._selected_values[0]  # noqa: SLF001
        )

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
        selected_thread = next(
            t
            for t in self.threads
            if str(t.thread_id) == self.thread_select._selected_values[0]  # noqa: SLF001
        )

        day = self.get_select_value(self.day_select)
        day = int(day) if day else 7

        if day == 7:  # noqa: PLR2004
            # 7 is for when user doesn't want a day set
            day = None

        active = self.get_select_value(self.active_select)
        active = bool(int(active)) if active is not None else True

        self.spoiler_threads.update(
            {"_id": selected_thread._id},  # noqa: SLF001
            {"$set": {"active": active, "day": day}},
        )

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
