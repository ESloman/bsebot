"""Tests our BSE View."""

import discord
import pytest

from discordbot.views.bseview import BSEView
from tests.mocks import discord_mocks


class TestBSEView:
    """Tests our BSEView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self._message = discord_mocks.MessageMock()

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = BSEView()
        assert view.timeout == 60
        assert view.disable_on_timeout
        assert isinstance(view, discord.ui.View)

    async def test_init_with_kwargs(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = BSEView(timeout=90, disable_on_timeout=False)
        assert view.timeout == 90
        assert not view.disable_on_timeout
        assert isinstance(view, discord.ui.View)

    async def test_on_timeout(self) -> None:
        """Tests timeout."""
        view = BSEView()

        # add a dummy message to the view
        view.message = self._message
        # add some children
        view.add_item(discord.ui.Button())
        view.add_item(discord.ui.Button())

        await view.on_timeout()
        assert len(view.children)
        for child in view.children:
            assert child.disabled
