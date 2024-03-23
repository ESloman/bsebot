"""Mocks for slash commands."""


class CloseABetMock:
    def __init__(self, client, guild_ids: list[int]) -> None:  # noqa: ANN001
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
        """


class PlaceABetMock:
    def __init__(self, client, guild_ids: list[int]) -> None:  # noqa: ANN001
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
        """
