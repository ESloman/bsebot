
import discord


class BaseMessageAction():
    """
    Base message action class to be inherited from
    """
    def __init__(self, client: discord.Bot) -> None:
        self.client = client

    async def pre_condition(self, message: discord.Message, message_type: list) -> bool:
        """
        Empty precondition function
        Should return True if an _should_ be fun and False if not

        Args:
            message (discord.Message): the discord Messageto check
            message_type (list): precalculated message type to help with precondition check

        Raises:
            NotImplementedError: if not implemented

        Returns:
            bool: whether to run the action or not
        """
        raise NotImplementedError

    async def run(self, message: discord.Message) -> None:
        """
        Empty action function
        The action to run if the precondition is true

        Args:
            message (discord.Message): the message to act on

        Raises:
            NotImplementedError:
        """
        raise NotImplementedError