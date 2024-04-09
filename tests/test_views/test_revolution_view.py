"""Tests our revolution views."""

import datetime
from unittest import mock
from zoneinfo import ZoneInfo

import pytest

from discordbot.views.revolution import RevolutionView
from mongo import interface
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

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    async def test_init(self, event_data: dict) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data))

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    async def test_toggle_stuff(self, event_data: dict) -> None:
        """Tests toggle stuff.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data))
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
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data))
        button = discord_mocks.ButtonMock(label=view._SAVE_THYSELF_BUTTON_TEXT)
        interaction = discord_mocks.InteractionMock(123456)
        assert await view._handle_save_thyself_button_checks(interaction, button, 123456, 123456)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    async def test_save_thyself_button_checks_incorrect_king_usage(self, event_data: dict) -> None:
        """Tests the save_thyself_button_checks.

        Should return False as the King is using the wrong button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data))
        button = discord_mocks.ButtonMock(label="Some other text.")
        interaction = discord_mocks.InteractionMock(123456)
        assert not await view._handle_save_thyself_button_checks(interaction, button, 123456, 123456)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    async def test_save_thyself_button_checks_incorrect_user_usage(self, event_data: dict) -> None:
        """Tests the save_thyself_button_checks.

        Should return False as a user is trying to press the KING button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        view = RevolutionView(self.bsebot, RevolutionEvent.make_data_class(event_data))
        button = discord_mocks.ButtonMock(label=view._SAVE_THYSELF_BUTTON_TEXT)
        interaction = discord_mocks.InteractionMock(123456)
        assert not await view._handle_save_thyself_button_checks(interaction, button, 123456, 654321)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    @pytest.mark.parametrize("key", ["revolutionaries", "supporters"])
    async def test_handle_non_save_thyself_buttons(self, event_data: dict, key: str) -> None:
        """Tests the handle_non_save_thyself_buttons.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        interaction = discord_mocks.InteractionMock(123456)
        for user in [*_event.users, 123456789]:
            if "locked_in" in event_data:
                event_data["locked_in"].append(user)
            expected = user not in getattr(_event, key)
            if expected and user in event_data.get("locked_in", []):
                expected = False
            assert expected == await view._handle_non_save_thyself_buttons(
                interaction, user, RevolutionEvent.make_data_class(event_data), key
            )

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    async def test_handle_overthrow_support_buttons(self, event_data: dict) -> None:
        """Tests the handle_overthrow_support_buttons.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        for user in [*_event.users, 123456789]:
            if "locked_in" in event_data:
                event_data["locked_in"].append(user)
            if user == 123456789:
                event_data["neutrals"].append(user)
            for key, other_key in (("revolutionaries", "supporters"), ("supporters", "revolutionaries")):
                faction_chance = 15 if key == "revolutionaries" else -15
                view._handle_overthrow_support_buttons(
                    RevolutionEvent.make_data_class(event_data).unfrozen(), user, key, other_key, faction_chance
                )

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    async def test_handle_impartial_button(self, event_data: dict) -> None:
        """Tests the handle_impartial_button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        for user in [*_event.users, 123456789]:
            if user == 123456789:
                event_data["neutrals"].append(user)
            view._handle_impartial_button(RevolutionEvent.make_data_class(event_data).unfrozen(), user)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_handle_save_thyself_button(self, event_data: dict) -> None:
        """Tests the handle_save_thyself_button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        interaction = discord_mocks.InteractionMock(_event.guild_id)
        msg = view._handle_save_thyself_button(_event.unfrozen(), _event.king, interaction)
        assert isinstance(msg, str)
        assert str(_event.king) in msg

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_revolution_button_logic_not_open(self, event_data: dict) -> None:
        """Tests the revolution_button_logic closed.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        event_data["open"] = False
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        interaction = discord_mocks.InteractionMock(_event.guild_id)
        button = discord_mocks.ButtonMock(label="doesn't matter")
        with mock.patch.object(view.revolutions, "get_event", return_value=_event):
            await view._revolution_button_logic(interaction, button)
        for child in view.children:
            # should all be disabled after exiting
            assert child.disabled

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_revolution_button_logic_expired(self, event_data: dict) -> None:
        """Tests the revolution_button_logic expired.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        event_data["open"] = True
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        interaction = discord_mocks.InteractionMock(_event.guild_id)
        button = discord_mocks.ButtonMock(label="doesn't matter")
        with mock.patch.object(view.revolutions, "get_event", return_value=_event):
            await view._revolution_button_logic(interaction, button)
        for child in view.children:
            # should all be disabled after exiting
            assert child.disabled

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_revolution_button_logic_check_fail(self, event_data: dict) -> None:
        """Tests the revolution_button_logic with a failed button check.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        event_data["open"] = True
        event_data["expired"] = datetime.datetime.now(tz=ZoneInfo("UTC")) + datetime.timedelta(hours=6)
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        interaction = discord_mocks.InteractionMock(_event.guild_id)
        button = discord_mocks.ButtonMock(label="something else")
        with (
            mock.patch.object(view.revolutions, "get_event", return_value=_event),
            mock.patch.object(view, "_handle_save_thyself_button_checks", return_value=False) as func,
        ):
            await view._revolution_button_logic(interaction, button)
            assert func.call_count == 1

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_revolution_button_logic_other_buttons_fail(self, event_data: dict) -> None:
        """Tests the revolution_button_logic with a failed button check.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        event_data["open"] = True
        event_data["expired"] = datetime.datetime.now(tz=ZoneInfo("UTC")) + datetime.timedelta(hours=6)
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        interaction = discord_mocks.InteractionMock(_event.guild_id)
        button = discord_mocks.ButtonMock(label="OVERTHROW")
        for val in (True, False):
            with (
                mock.patch.object(view.revolutions, "get_event", return_value=_event),
                mock.patch.object(view, "_handle_non_save_thyself_buttons", return_value=val) as _func,
                mock.patch.object(view, "_handle_save_thyself_button_checks", return_value=True),
            ):
                await view._revolution_button_logic(interaction, button)
                assert _func.call_count == 1

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_revolution_button_logic(self, event_data: dict) -> None:
        """Tests the revolution_button_logic with a failed button check.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        event_data["open"] = True
        event_data["expired"] = datetime.datetime.now(tz=ZoneInfo("UTC")) + datetime.timedelta(hours=6)
        _event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionView(self.bsebot, _event)
        for user in _event.users:
            interaction = discord_mocks.InteractionMock(_event.guild_id, user)
            for button_label in ("OVERTHROW", "SUPPORT THE KING", "Impartial", "Save THYSELF"):
                button = discord_mocks.ButtonMock(label=button_label)
                with (
                    mock.patch.object(view.revolutions, "get_event", return_value=_event),
                    mock.patch.object(view, "_handle_non_save_thyself_buttons", return_value=True),
                    mock.patch.object(view, "_handle_save_thyself_button_checks", return_value=True),
                    mock.patch.object(view, "_handle_save_thyself_button", return_value=""),
                ):
                    await view._revolution_button_logic(interaction, button)
