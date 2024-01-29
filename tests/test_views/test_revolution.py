"""Tests our revolution views."""

import pytest

from discordbot.utilities import PlaceHolderLogger
from discordbot.views.revolution import RevolutionView
from mongo.bseticketedevents import RevolutionEvent
from tests.mocks import bsebot_mocks, interface_mocks


class TestRevolutionView:
    """Tests our RevolutionView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    async def test_init(self, event_data: dict) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data), self.logger)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    async def test_toggle_stuff(self, event_data: dict) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data), self.logger)
        for toggle in (True, False):
            view.toggle_stuff(toggle)
            for child in view.children:
                assert child.disabled == toggle
