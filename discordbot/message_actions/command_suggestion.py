"""Command suggest message action class."""

import re
from logging import Logger

import discord

from discordbot.bsebot import BSEBot
from discordbot.message_actions.base import BaseMessageAction


class CommandSuggest(BaseMessageAction):
    """Command suggest message action.

    Will provide easy links to command when used in free text.
    """

    def __init__(self, client: BSEBot, logger: Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): our BSEBot client
            logger (Logger): our logger
        """
        super().__init__(client, logger)

    async def pre_condition(self, message: discord.Message, _: list[str]) -> bool:
        """Checks that a message contains `/COMMAND_NAME` and that it's a valid command name.

        Args:
            message (discord.Message): message to check
            _ (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        if message.author.bot:
            # don't trigger on ourselves
            return False

        if "/" not in message.content:
            return False

        if matches := re.findall(r"(\/[a-z0-9_]+)[\s`_*]", message.content.lower()):
            app_commands = self.client.application_commands
            command_names = [app.name for app in app_commands]

            for _match in matches:
                match_name = _match.strip("/")
                if match_name in command_names:
                    # found at least one match - we're good
                    return True
            # return False if we find nothing that matches
            return False
        return False

    async def run(self, message: discord.Message) -> None:
        """Replies to the user with a list of commands that they can click on.

        Args:
            message (discord.Message): the message to action
        """
        matches = re.findall(r"\/[a-z0-9_]+", message.content.lower())
        app_commands = self.client.application_commands
        command_names = [app.name for app in app_commands]
        app_map = {app.name: app for app in app_commands}

        msg = "Looks like your message contains command references:\n"

        for _match in matches:
            match_name = _match.strip("/")
            if match_name in command_names:
                app_command = app_map[match_name]
                msg += f"- {app_command.mention}\n"

        msg += "\n" f"For more information on commands, use {app_map['help'].mention}."

        await message.reply(content=msg, suppress=True)
