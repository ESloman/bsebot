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

    async def test_update(self) -> None:
        """Tests update method."""
        view = BSEView()
        with pytest.raises(NotImplementedError):
            await view.update(None)

    async def test_toggle_item(self) -> None:
        """Tests toggle_item."""
        view = BSEView()

        select = discord.ui.Select(options=[discord.SelectOption(label=str(x), value=str(x)) for x in range(5)])
        button = discord.ui.Button(label="Test")
        view.add_item(button)
        view.add_item(select)

        view.toggle_item(True, discord.ui.Button)
        assert button.disabled
        assert not select.disabled
        view.toggle_item(False, discord.ui.Button)
        assert not select.disabled
        assert not button.disabled

    async def test_toggle_item_no_items(self) -> None:
        """Tests toggle_item with no children."""
        view = BSEView()
        view.toggle_item(True, discord.ui.Button)

    async def test_toggle_button(self) -> None:
        """Tests toggle_button."""
        view = BSEView()

        button = discord.ui.Button(label="Test")
        submit_button = discord.ui.Button(label="Submit")
        view.add_item(button)
        view.add_item(submit_button)

        view.toggle_button(True, "Submit")
        assert not button.disabled
        assert submit_button.disabled
        view.toggle_button(False, "Submit")
        assert not button.disabled
        assert not submit_button.disabled

    async def test_toggle_button_no_items(self) -> None:
        """Tests toggle_button with no children."""
        view = BSEView()
        view.toggle_button(True)

    async def test_get_select_value(self) -> None:
        """Tests get_select_value returns the selected value."""
        view = BSEView()

        select = discord.ui.Select(options=[discord.SelectOption(label=str(x), value=str(x)) for x in range(5)])

        interaction = discord_mocks.InteractionMock()
        interaction.data["values"] = ["2"]
        select.refresh_state(interaction)

        value = view.get_select_value(select)
        assert value == "2"

    async def test_get_select_value_none(self) -> None:
        """Tests get_select_value returns None with nothing selected and no default."""
        view = BSEView()

        select = discord.ui.Select(options=[discord.SelectOption(label=str(x), value=str(x)) for x in range(5)])
        value = view.get_select_value(select)
        assert value is None

    async def test_get_select_value_default(self) -> None:
        """Tests get_select_value returns default value with nothing selected."""
        view = BSEView()

        select = discord.ui.Select(
            options=[discord.SelectOption(label=str(x), value=str(x), default=x == 2) for x in range(5)]
        )
        value = view.get_select_value(select)
        assert value == "2"
