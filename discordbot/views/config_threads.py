import discord
from discordbot.selects.threadconfig import ThreadConfigSelect, ThreadActiveSelect, ThreadDaySelect


from mongo.bsedataclasses import SpoilerThreads
from mongo.datatypes import Thread


class ThreadConfigView(discord.ui.View):
    def __init__(
        self,
        threads: list[Thread]
    ):
        super().__init__(timeout=120)

        self.spoiler_threads = SpoilerThreads()

        threads = [t for t in threads if t["active"]]
        self.threads = threads
        self.thread_select = ThreadConfigSelect(threads)
        self.add_item(self.thread_select)

        self.active_select = ThreadActiveSelect()
        self.add_item(self.active_select)

        self.day_select = ThreadDaySelect()
        self.add_item(self.day_select)

    async def update(self):
        # updates all the selects with new values
        print(self.thread_select._selected_values)
        selected_thread = [t for t in self.threads if str(t["thread_id"]) == self.thread_select._selected_values[0]][0]

        for opt in self.day_select.options:
            opt.default = False

        if selected_thread["day"]:
            for opt in self.day_select.options:
                if int(opt.value) == selected_thread["day"]:
                    opt.default = True
                    break

        self.active_select.disabled = False
        self.day_select.disabled = False

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        selected_thread = [t for t in self.threads if str(t["thread_id"]) == self.thread_select._selected_values[0]][0]

        try:
            day = int(self.day_select._selected_values[0])
        except (IndexError, AttributeError):
            # look for default as user didn't select one explicitly
            for opt in self.day_select.options:
                if opt.default:
                    day = int(opt.value)
                    break

        if day == 7:
            # 7 is for when user doesn't want a day set
            day = None

        try:
            active = bool(int(self.active_select._selected_values[0]))
        except (IndexError, AttributeError):
            # user didn't select a value
            # true is default here
            active = True

        self.spoiler_threads.update(
            {"_id": selected_thread["_id"]},
            {"$set": {"active": active, "day": day}}
        )

        await interaction.response.edit_message(
            content="Thread updated.",
            view=None,
            delete_after=10
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
