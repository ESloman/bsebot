"""Tests our Wrapped view."""

from discordbot.views.wrapped import WrappedView
from tests.mocks import discord_mocks


class TestWrappedView:
    """Tests our WrappedView view."""

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = WrappedView()

    async def test_button_callback(self) -> None:
        """Tests button callback."""
        view = WrappedView()
        interaction = discord_mocks.InteractionMock(123456)
        await view.share_callback.callback(interaction)

    async def test_button_callback_twice(self) -> None:
        """Tests button callback."""
        view = WrappedView()
        interaction = discord_mocks.InteractionMock(123456)
        await view.share_callback.callback(interaction)
        await view.share_callback.callback(interaction)
