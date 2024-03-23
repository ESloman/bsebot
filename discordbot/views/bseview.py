"""BSEView class that all views can inherit from."""

import contextlib

import discord
from slomanlogger import SlomanLogger


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
        self.logger = SlomanLogger("bsebot")

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

    @staticmethod
    def get_select_value(select: discord.ui.Select) -> str | None:
        """Wrapper for getting a single value out of a select.

        Args:
            select (discord.ui.Select): the select

        Returns:
            str | None: the found value or None
        """
        try:
            value = select._selected_values[0]  # noqa: SLF001
        except (IndexError, AttributeError, TypeError):
            try:
                value = select.values[0]
            except (IndexError, AttributeError, TypeError):
                try:
                    value = next(o for o in select.options if o.default).value
                except StopIteration:
                    value = None
        return value

    def toggle_item(self, disabled: bool, select_type: type) -> None:
        """Toggles an item by type.

        Args:
            disabled (bool): whether the item should be disabled or not
            select_type (type): the type to use as an identifier
        """
        for child in self.children:
            if type(child) is select_type:
                child.disabled = disabled
                break

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
