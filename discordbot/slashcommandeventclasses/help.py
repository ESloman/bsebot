"""Help slash command."""

import datetime
import logging

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class Help(BSEddies):
    """Class for handling `/help` commands."""

    def __init__(
        self, client: BSEBot, guild_ids: list, logger: logging.Logger, command_list: list[BSEddies] | None = None
    ) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
            command_list (list[BSEddies] | None): the list of commands
        """
        super().__init__(client, guild_ids, logger)
        self.command_list = command_list
        self.activity_type = ActivityTypes.HELP
        self.help_string = "This command"
        self.command_name = "help"

    async def help(self, ctx: discord.ApplicationContext) -> None:  # noqa: A003
        """Basic view method for handling help slash commands.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.HELP)

        available_commands = [com.activity_type for com in self.command_list]

        # get all activities from the last couple of months
        now = datetime.datetime.now()
        now += datetime.timedelta(hours=1)
        threshold = now - datetime.timedelta(days=60)
        activities = self.activities.get_guild_activities_by_timestamp(ctx.guild_id, threshold, now)

        activities = [act for act in activities if act.type in available_commands]

        app_commands = self.client.application_commands

        counts = {}
        for act in activities:
            if act.type not in counts:
                counts[act.type] = 0
            counts[act.type] += 1

        sorted_types = sorted(counts, key=lambda x: counts[x], reverse=True)
        if len(sorted_types) > 10:  # noqa: PLR2004
            sorted_types = sorted_types[:10]

        message = "# Help\n\nListed below are some of the more popular commands.\n"
        for act_type in sorted_types:
            # need to get the SlashCommand class
            # and the application command object
            try:
                command = next(com for com in self.command_list if com.activity_type == act_type)
                app_command = next(app_com for app_com in app_commands if app_com.name == command.command_name)
                help_string = f"- {app_command.mention} - {command.help_string}"
                message += "\n"
                message += help_string
            except (IndexError, AttributeError, TypeError):
                continue

        message += (
            "\n\n"
            "For more commands you can check the wiki [here](https://github.com/ESloman/bsebot/wiki/Commands).\n"
            "[Repo link](https://github.com/ESloman/bsebot)."
        )

        await ctx.respond(content=message, ephemeral=True)
