"""Tests our stats views."""

from unittest import mock

import pytest

from discordbot.slashcommandeventclasses.stats import Stats
from discordbot.views.stats import StatsView
from tests.mocks import bsebot_mocks, discord_mocks


@pytest.mark.xfail
class TestStatsView:
    """Tests our StatsView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

        self.stats = Stats(self.bsebot)

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = StatsView(self.stats)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = StatsView(self.stats)
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("mode", ["quick", "server", "other"])
    async def test_update(self, mode: str) -> None:
        """Tests update method."""
        view = StatsView(self.stats)
        interaction = discord_mocks.InteractionMock()
        interaction.data["values"] = [mode]
        view.stats_mode.refresh_state(interaction)
        await view.update(interaction)

    @pytest.mark.parametrize("mode", ["quick", "server", "other"])
    async def test_submit_callback(self, mode: str) -> None:
        """Tests submit_callback method."""
        view = StatsView(self.stats)
        interaction = discord_mocks.InteractionMock()
        interaction.data["values"] = [mode]
        view.stats_mode.refresh_state(interaction)
        with mock.patch.object(view.stats_class, "stats_quick"), mock.patch.object(view.stats_class, "stats_server"):
            await view.submit_button_callback.callback(interaction)
