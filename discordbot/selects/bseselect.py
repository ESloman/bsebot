"""Our BSE Select class."""

from discord.ui import Select

from discordbot.views.bseview import BSEView


class BSESelect(Select):
    """BSE Select class.

    Effectively, just exists to provide a typed wrapper around the self.view property.
    """

    def __init__(self, *args: tuple[any], **kwargs: dict[str, any]) -> None:
        """Initialisation method."""
        super().__init__(*args, **kwargs)

    @property
    def view(self) -> BSEView:
        """The underlying view for this item."""
        return self._view
