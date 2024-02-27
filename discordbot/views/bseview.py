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

    async def update(self, interaction: discord.Interaction) -> None:
        """Method for updating the view.

        Needs to be implemented by the subclasses.
        """
        raise NotImplementedError

    async def on_timeout(self) -> None:
        """View timeout function.

        Is invoked when the message times out.
        """
        self.disable_all_items()

        with contextlib.suppress(discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            await self.message.edit(content="This command timed out - please place another one.", view=None)

    def toggle_button(self, disabled: bool, label: str = "Submit") -> None:
        """Toggles a button.

        Args:
            disabled (bool): whether the button should be disabled or not
            label (str): the button label to use as an identifier
        """
        for child in self.children:
            if type(child) is discord.ui.Button and child.label == label:
                child.disabled = disabled
                break
