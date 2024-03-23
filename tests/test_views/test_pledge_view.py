"""Tests our pledge views."""

import pytest

from discordbot.views.pledge import PledgeView
from tests.mocks import bsebot_mocks, discord_mocks


class TestPledgeView:
    """Tests our PledgeView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

    @pytest.mark.parametrize("current", [0, 1, 2, None])
    async def test_init(self, current: int | None) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = PledgeView(current)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = PledgeView()
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)
