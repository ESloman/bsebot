
import asyncio
import datetime
from logging import Logger

from discord.ext import tasks

from apis.github import GitHubAPI
from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class ReleaseChecker(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        github_api: GitHubAPI
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.release_checker
        self.last_release_name = None
        self.github = github_api

        self.task.start()

    @tasks.loop(minutes=60)
    async def release_checker(self):
        """
        Task to check github releases and post release notes when we get a new one
        """

        now = datetime.datetime.now()

        if now.hour != 12:
            return

        release_ret = self.github.get_latest_release("ESloman", "bsebot")
        release_info = release_ret.json()
        release_name = release_info["name"]
        release_body = release_info["body"]

        # process body now so we only have to do it once
        split_body = release_body.split("\n")
        body = f"A new release: **{release_name}** has been published."
        body += "\nThis incorporates the latest changes made since the last release. "
        body += "Below are the generated change notes.\n\n"

        bodies = []
        for part in split_body:
            body += part
            body += "\n"
            if len(body) > 1900:
                bodies.append(body)
                body = ""

        bodies.append(body)

        if not self.last_release_name:
            self.last_release_name = release_name
        elif self.last_release_name == release_name:
            # same as last one - just skip
            return
        else:
            # new release name to process
            self.last_release_name = release_name

        async for guild in self.bot.fetch_guilds():
            guild_db = self.guilds.get_guild(guild.id)

            if not guild_db.get("release_notes"):
                # release notes isn't set to True - skipping
                continue

            last_release_ver = guild_db.get("release_ver")
            if not last_release_ver:
                self.guilds.set_latest_release(guild.id, release_name)
                last_release_ver = release_name

            if last_release_ver == release_name:
                # same as last release name
                continue

            channel = await self.bot.fetch_channel(guild_db["channel"])
            for _body in bodies:
                await channel.send(content=_body, silent=True, suppress=True)

            self.guilds.set_latest_release(guild.id, release_name)

    @release_checker.before_loop
    async def before_release_checker(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
