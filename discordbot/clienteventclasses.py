import discord

from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserBets, UserPoints


class BaseEvent(object):
    def __init__(self, client, guild_ids, beta_mode=False):
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.client = client
        self.guild_ids = guild_ids
        self.beta_mode = beta_mode
        self.embed_manager = EmbedManager()


class OnReadyEvent(BaseEvent):
    def __init__(self, client, guild_ids, beta_mode=False):
        super().__init__(client, guild_ids, beta_mode=beta_mode)
        self.client = client

    def on_ready(self):
        """
        Method called for on_ready event. Makes sure we have an entry for every user in each guild.
        :return:
        """
        print("Checking guilds for members")
        for guild_id in self.guild_ids:
            guild = self.client.get_guild(guild_id)
            print(f"Checking guild: {guild.id} - {guild.name}")
            for member in guild.members:
                if not member.bot:
                    print(f"Checking {member.id} - {member.name}")
                    user = self.user_points.find_user(member.id, guild.id)
                    if not user:
                        self.user_points.create_user(member.id, guild.id)
                        print(f"Creating new user entry for {member.id} - {member.name} for {guild.id} - {guild.name}")
        print("Finished member check.")


class OnReactionAdd(BaseEvent):
    """
    Class for handling on_reaction_add events from Discord
    """
    def __init__(self, client, guild_ids, beta_mode=False):
        super().__init__(client, guild_ids, beta_mode=beta_mode)

    async def handle_reaction_event(
            self,
            message: discord.Message,
            guild: discord.Guild,
            channel: discord.TextChannel,
            reaction_emoji: str,
            user: discord.User
    ):
        """
        Main event for handling reaction events. This method simply filters out
        stuff that we don't care about and calls other methods to handle the stuff we do.
        :param message:
        :param guild:
        :param channel:
        :param reaction_emoji:
        :param user:
        :return:
        """
        if user.bot:
            return

        if guild.id not in self.guild_ids:
            return

        if self.beta_mode and channel.id != 809773876078575636:
            msg = f"These features are in BETA mode and this isn't a BETA channel."
            if not user.dm_channel:
                await user.create_dm()
            try:
                await user.send(content=msg)
            except discord.errors.Forbidden:
                pass
            return

        if message.content and "BSEddies Leaderboard" in message.content and reaction_emoji == u"▶️":
            if not message.author.bot:
                return

            content = self.embed_manager.get_leaderboard_embed(guild, None)
            await message.edit(content=content)
            return

        if message.embeds and "Bet ID" in message.embeds[0].description:
            embed = message.embeds[0]  # type: discord.Embed
            bet_id = embed.description.replace("Bet ID: ", "")
            bet = self.user_bets.get_bet_from_id(guild.id, bet_id)

            link = f"https://discordapp.com/channels/{guild.id}/{channel.id}/{message.id}"

            if not bet["active"]:
                msg = f"Your reaction on **Bet {bet_id}** _({link})_ failed as the bet is closed for new bets."
                if not user.dm_channel:
                    await user.create_dm()
                try:
                    await user.send(content=msg)
                except discord.errors.Forbidden:
                    pass
                await message.remove_reaction(reaction_emoji, user)
                return

            if reaction_emoji not in bet['option_dict']:
                msg = f"Your reaction on **Bet {bet_id}** _({link})_ failed as that reaction isn't a valid outcome."
                if not user.dm_channel:
                    await user.create_dm()
                try:
                    await user.send(content=msg)
                except discord.errors.Forbidden:
                    pass
                await message.remove_reaction(reaction_emoji, user)
                return

            ret = self.user_bets.add_better_to_bet(bet_id, guild.id, user.id, reaction_emoji, 1)
            if ret["success"]:
                print("bet successful!")
                new_bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
                embed = self.embed_manager.get_bet_embed(guild, bet_id, new_bet)
                await message.edit(embed=embed)
            await message.remove_reaction(reaction_emoji, user)
