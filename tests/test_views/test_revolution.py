"""Tests our revolution views."""

import pytest

from discordbot.utilities import PlaceHolderLogger
from discordbot.views.revolution import RevolutionView
from mongo.bseticketedevents import RevolutionEvent
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


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
        """Tests toggle stuff.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data), self.logger)
        for toggle in (True, False):
            view.toggle_stuff(toggle)
            for child in view.children:
                assert child.disabled == toggle

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    async def test_save_thyself_button_checks(self, event_data: dict) -> None:
        """Tests the save_thyself_button_checks.

        Should return True as the King is using the right button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data), self.logger)
        button = discord_mocks.ButtonMock(label=view._SAVE_THYSELF_BUTTON_TEXT)
        interaction = discord_mocks.InteractionMock(123456)
        assert await view._handle_save_thyself_button_checks(interaction, button, 123456, 123456)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    async def test_save_thyself_button_checks_incorrect_king_usage(self, event_data: dict) -> None:
        """Tests the save_thyself_button_checks.

        Should return False as the King is using the wrong button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data), self.logger)
        button = discord_mocks.ButtonMock(label="Some other text.")
        interaction = discord_mocks.InteractionMock(123456)
        assert not await view._handle_save_thyself_button_checks(interaction, button, 123456, 123456)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    async def test_save_thyself_button_checks_incorrect_user_usage(self, event_data: dict) -> None:
        """Tests the save_thyself_button_checks.

        Should return False as a user is trying to press the KING button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data), self.logger)
        button = discord_mocks.ButtonMock(label=view._SAVE_THYSELF_BUTTON_TEXT)
        interaction = discord_mocks.InteractionMock(123456)
        assert not await view._handle_save_thyself_button_checks(interaction, button, 123456, 654321)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    async def test_handle_non_save_thyself_buttons(self, event_data: dict) -> None:
        """Tests the handle_non_save_thyself_buttons.

        Should return True as the King is using the right button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event, self.logger)
        interaction = discord_mocks.InteractionMock(123456)
        for user in _event.users:
            if "locked_in" in event_data:
                event_data["locked_in"].append(user)
            for key in ("revolutionaries", "supporters"):
                expected = user not in getattr(_event, key)
                if expected and user in event_data.get("locked_in", []):
                    expected = False
                assert expected == await view._handle_non_save_thyself_buttons(
                    interaction, user, RevolutionEvent.make_data_class(event_data), key
                )
