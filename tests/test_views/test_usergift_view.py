"""Tests our GiftUserEddiesView view."""

from unittest import mock

import pytest

from discordbot.slashcommandeventclasses.gift import Gift
from discordbot.views.usergift import GiftUserEddiesView
from tests.mocks import bsebot_mocks, discord_mocks


@pytest.mark.xfail
class TestGiftUserEddiesView:
    """Tests our GiftUserEddiesView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

        self.gift = Gift(self.bsebot)

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = GiftUserEddiesView(100, discord_mocks.MemberMock(123456), self.gift)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = GiftUserEddiesView(100, discord_mocks.MemberMock(123456), self.gift)
        interaction = discord_mocks.InteractionMock(654321)
        await view.cancel_callback(None, interaction)

    async def test_submit_callback(self) -> None:
        """Tests submit callback."""
        view = GiftUserEddiesView(100, discord_mocks.MemberMock(123456), self.gift)
        interaction = discord_mocks.InteractionMock(654321)

        # force our select to have data
        interaction.data["values"] = ["50"]
        view.gift_amount.refresh_state(interaction)

        with mock.patch.object(self.gift, "gift_eddies"):
            await view.submit_button_callback.callback(interaction)
