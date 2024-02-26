"""BSEView class that all views can inherit from."""

import contextlib

import discord


class BSEView(discord.ui.View):
    """BSE View class."""

    def __init__(
        self, *args: tuple[any], timeout: int = 60, disable_on_timeout: bool = True, **kwargs: dict[str, any]
    ) -> None:
        """Initialisation method.

        Args:
            args (tuple[any]): args
            timeout (int): view timeout. Defaults to 60.
            disable_on_timeout (bool): whether to disable the view on timeout. Defaults to True.
            kwargs (dict[str, any]): kwargs
        """
        super().__init__(*args, timeout=timeout, disable_on_timeout=disable_on_timeout, **kwargs)

    async def on_timeout(self) -> None:
        """View timeout function.

        Is invoked when the message times out.
        """
        self.disable_all_items()

        with contextlib.suppress(discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            await self.message.edit(content="This command timed out - please place another one.", view=None)
