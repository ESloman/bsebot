import asyncio
import datetime
import re

import a2s
import asyncssh
import discord
from discord.ext import tasks, commands
from mcstatus import MinecraftServer

from apis.awsapi import AWSAPI
from discordbot.constants import AWS_GAME_SERVER_INSTANCE, BSE_SERVER_ID, BSE_SERVER_INFO_CHANNEL
from discordbot.embedmanager import EmbedManager
from mongo.bsegames import GameServers, GameServerInfo


class ServerInfo(commands.Cog):
    def __init__(self, bot: discord.Client, logger):
        self.bot = bot
        self.embed_manager = EmbedManager(logger)
        self.logger = logger
        self.aws = AWSAPI()
        self.game_servers = GameServers()
        self.game_server_info = GameServerInfo()
        self.server_info.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.server_info.cancel()

    @tasks.loop(seconds=15)
    async def server_info(self):
        """
        Constantly checks to make sure that all events have been closed properly or raised correctly
        :return:
        """
        guild = self.bot.get_guild(BSE_SERVER_ID)
        channel = guild.get_channel(BSE_SERVER_INFO_CHANNEL)

        self.logger.info("Quering amazon server")
        instance = self.aws.get_instance(AWS_GAME_SERVER_INSTANCE)

        status = instance.state["Name"]

        if status == "running":

            # increase the interval to get more accurate server info
            if self.server_info.seconds == 0:
                self.server_info.change_interval(hours=0, seconds=15)

            status_emoji = ":green_circle:"
        elif status == "stopped":

            # reduce the interval to prevent too many api calls when accuracy isn't needed
            if self.server_info.seconds == 15:
                self.server_info.change_interval(hours=1, seconds=0)

            status_emoji = ":red_circle:"
        else:
            status_emoji = ":yellow_circle:"

        ip = instance.public_ip_address
        launch_time = instance.launch_time
        if launch_time:
            up_time = datetime.datetime.now(datetime.timezone.utc) - launch_time
        else:
            up_time = None

        message = (
            "**BSE Server Info**\n\n"
            f"**IP Address**: `{ip}`\n"
            f"**Status**: {status_emoji} `{status}`"
        )

        if up_time and status != "stopped":
            message += f"\n**Uptime**: `{up_time}`"

        if status == "running":
            try:
                async with asyncssh.connect("awsgames") as conn:
                    # load average
                    result = await conn.run("uptime", check=True)
                    load_average = re.findall("(?<=load average: ).*(?=\\n)", result.stdout)[0]
                    message += f"\n**Load average**: `{load_average}`"

                    # memory usage
                    mem_cmd = "awk '/^Mem/ {printf(\"%u%%\", 100*$3/$2);}' <(free -m)"
                    result = await conn.run(mem_cmd, check=True)
                    memory_usage = result.stdout
                    message += f"\n**Memory usage**: `{memory_usage}`"

                    # disk space free
                    disk_cmd = "df --output=pcent /dev/root | tr -dc '0-9'"
                    result = await conn.run(disk_cmd, check=True)
                    disk_space = f"{result.stdout}%"
                    message += f"\n**Disk space usage**: `{disk_space}`"
            except ConnectionRefusedError:
                self.logger.info(f"SSH server not yet running")

        players_connected = 0
        all_game_servers = self.game_servers.get_all_game_servers()

        if all_game_servers:
            message += "\n\n**Services**:\n"

        for server in all_game_servers:
            message += f"\n*----*\n"
            s_message = f"`Game`: _{server['game'].title()}_\n`Server`: _{server['name']}_"
            if status != "running":
                s_message += f"\n`Status`: :red_circle: _Offline_"
                message += s_message
                continue

            if server["type"] == "steam":
                add_details, plys = await self.format_steam_server(server)
                s_message += add_details
                players_connected += plys
            elif server["type"] == "minecraft":
                add_details, plys = await self.format_minecraft_server(server)
                s_message += add_details
                players_connected += plys

            message += s_message
            message += "\n"

        self.game_server_info.update_player_count(players_connected)

        if players_connected == 0 and up_time.total_seconds() > 900 and not self.game_server_info.get_debug_mode():
            self.aws.stop_instance(AWS_GAME_SERVER_INSTANCE)

        message += f"\n\nThis message is updated every minute or so when the server is online."

        message_to_edit = await channel.fetch_message(823122665530982400)
        await message_to_edit.edit(content=message)

    @staticmethod
    async def format_steam_server(server):
        """

        :param server:
        :return:
        """
        addr = (server["ip"], server["rcon_port"])
        try:
            info = await a2s.ainfo(addr)
        except (asyncio.TimeoutError, ConnectionRefusedError):
            info = None

        if not info:
            return f"\n`Status`: :red_circle: _Offline_", 0

        server_message = (
            f"\n`Status`: :green_circle: _Online_\n"
            f"`Port`: {server['port']}\n"
            f"`Player Count`: _{info.player_count}_"
        )

        if info.player_count > 0:
            players = await a2s.aplayers(addr)
            server_message += "\n`Players`:"
            for ply in players:
                server_message += f"\n - {ply.name or 'unknown'}"
        return server_message, info.player_count

    async def format_minecraft_server(self, server):
        """

        :param server:
        :return:
        """
        mc_server = MinecraftServer(server["dns"], server["port"])
        try:
            query = mc_server.query()
        except (asyncio.TimeoutError, ConnectionRefusedError):
            query = None
        except:
            self.logger.info("unknown exception")
            query = None

        if not query:
            return f"\n`Status`: :red_circle: _Offline_", 0

        server_message = (
            f"\n`Status`: :green_circle: _Online_\n"
            f"`Port`: {server['port']}\n"
            f"`Version`: _{query.software.version}_\n"
            f"`Player Count`: _{query.players.online}_"
        )

        if query.players.online > 0:
            server_message += "\n`Players`:"
            for ply in query.players.names:
                server_message += f"\n - {ply}"

        return server_message, query.players.online

    @server_info.before_loop
    async def before_server_info(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
