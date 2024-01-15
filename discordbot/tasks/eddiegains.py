"""Tasks for eddie gains."""

import asyncio
import datetime
import math
import re
from collections import Counter
from logging import Logger

import discord
from discord.ext import tasks

from discordbot import utilities
from discordbot.bot_enums import SupporterType, TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.constants import (
    CREATOR,
    GENERAL_CHAT,
    HUMAN_MESSAGE_TYPES,
    MESSAGE_TYPES,
    MESSAGE_VALUES,
    WORDLE_SCORE_REGEX,
    WORDLE_VALUES,
)
from discordbot.tasks.basetask import BaseTask
from mongo.datatypes.message import MessageDB, VCInteractionDB
from mongo.datatypes.user import UserDB


class EddieGainMessager(BaseTask):
    """Class for eddie gains task."""

    def __init__(
        self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask], start: bool = True
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task automatically or not. Defaults to True.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.eddie_distributer

        self.eddie_manager = BSEddiesManager(self.bot, guild_ids, self.logger, startup_tasks)
        if start:
            self.task.start()

    @tasks.loop(minutes=1)
    async def eddie_distributer(self) -> None | list[dict]:  # noqa: PLR0912, C901
        """Task that distributes daily eddies."""
        now = datetime.datetime.now()

        if now.hour != 7 or now.minute != 30:  # noqa: PLR2004
            return None

        data = []
        for guild_id in self.guild_ids:
            eddie_dict = self.eddie_manager.give_out_eddies(guild_id, real=True)
            data.append(eddie_dict)

            guild = await self.bot.fetch_guild(guild_id)  # type: discord.Guild
            guild_db = self.guilds.get_guild(guild_id)

            current_king_id = guild_db.king

            summary_message = "Eddie gain summary:\n"
            for user_id in eddie_dict:
                value = eddie_dict[user_id][0]
                breakdown = eddie_dict[user_id][1]
                tax = eddie_dict[user_id][2]

                if value == 0:
                    continue

                try:
                    user = await guild.fetch_member(int(user_id))  # type: discord.Member
                except discord.NotFound:
                    summary_message += f"\n- `{user_id}` :  **{value}** (tax: _{tax}_)"
                    continue

                summary_message += f"\n- `{user.display_name}` :  **{value}** (tax: _{tax}_)"
                text = f"Your daily salary of BSEDDIES is `{value}` (after tax).\n"

                if user_id == current_king_id:
                    text += f"You gained an additional `{tax}` from tax gains\n"
                else:
                    text += f"You were taxed `{tax}` by the KING.\n"

                text += "\nThis is based on the following amount of interactivity yesterday:"

                for key in sorted(breakdown):
                    text += f"\n- `{HUMAN_MESSAGE_TYPES[key]}`  :  **{breakdown[key]}**"

                    if key in {"vc_joined", "vc_streaming"}:
                        text += " seconds"

                self.logger.info("%s is gaining `%s eddies`", user.display_name, value)

                text += "\n\nWant to turn these notifications off? Use `/config` to disable."

                user_dict = self.user_points.find_user(int(user_id), guild.id)

                if user_dict.daily_eddies:
                    self.logger.info("Sending message to %s for %s", user.display_name, value)
                    try:
                        await user.send(content=text, silent=True)
                    except discord.Forbidden:
                        continue

            # make sure admin list is unique
            for user_id in {*guild_db.admins, CREATOR, guild_db.owner_id}:
                user_db = self.user_points.find_user(user_id, guild_id)

                if not user_db.daily_summary:
                    # not configured to send summary messages
                    continue

                user = await guild.fetch_member(user_id)  # type: discord.Member
                try:
                    await user.send(content=summary_message, silent=True)
                except discord.Forbidden:
                    # can't send DM messages to this user
                    self.logger.info("%s - %s", user.display_name, summary_message)
        return data

    @eddie_distributer.before_loop
    async def before_eddie_distributer(self) -> None:
        """We want to make sure the websocket is connected before we start sending requests via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)


class BSEddiesManager(BaseTask):
    """Class that _actually_ calculates eddies."""

    def __init__(self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask]) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            on_ready (OnReadyEvent): on ready event
            github_api (GitHubAPI): the authenticated Github api class
            place (PlaceBet): the place bet class
            close (CloseBet): the close bet class
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        # default minimum
        self.server_min = 4

    @staticmethod
    def get_datetime_objects(days: int = 1) -> tuple[datetime.datetime, datetime.datetime]:
        """Get's the datetime START and END of yesterday.

        Args:
            days (int): the number of days to go back. Defaults to 1.

        Returns:
            tuple[datetime.datetime, datetime.datetime]: start, end of day
        """
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=days)
        start = yesterday.replace(hour=0, minute=0, second=0)
        end = yesterday.replace(hour=23, minute=59, second=59)

        if not utilities.is_utc(now):
            # need to add UTC offset
            start = utilities.add_utc_offset(start)
            end = utilities.add_utc_offset(end)

        return start, end

    def _calc_eddies(self, counter: Counter[str, int], start: int = 4) -> float:
        """Loop over the message types and work out an amount of BSEddies the user will gain.

        Args:
            counter (Counter): the counter to use
            start (int): minimum eddies to start at

        Returns:
            float: the amount of eddies the user is going to gain
        """
        points = start
        for message_type in MESSAGE_TYPES:
            if val := counter.get(message_type):
                message_worth = MESSAGE_VALUES.get(message_type, 0)
                if not message_worth:
                    self.logger.debug("'%s' doesn't have a value associated with it - skipping", message_type)
                    continue
                t_points = val * message_worth
                points += t_points
                self.logger.info("%s for %s", t_points, message_type)
        return points

    def calc_individual(  # noqa: C901, PLR0913, PLR0912, PLR0915, PLR0917
        self,
        user: int,
        user_dict: UserDB,
        user_results: list[MessageDB | VCInteractionDB],
        user_reacted: list[MessageDB],
        user_reactions: list[MessageDB],
        start: datetime.datetime,
        end: datetime.datetime,
        guild_id: int,
        wordle_word: str | None = None,
        real: bool = False,
    ) -> tuple[int, dict[str, any]]:
        """Method that calculates the daily salary for a given individual.

        Needs all the data given to it.

        Args:
            user (int): The user ID of the user
            user_dict (User): The user database object
            user_results (list[MessageDB | VCInteractionDB]): list of user interactions
            user_reacted (list[MessageDB]): list of messages the user reacted to
            user_reactions (list[MessageDB]): list of messages the user had reactions on
            start (datetime.datetime): start time to calc eddies for
            end (datetime.datetime): end time to calc eddies for
            guild_id (int): the guild ID the user exists in
            wordle_word (str, optional): the wordle word for the day
            real (bool, optional): Whether to actually do operations. Defaults to False.

        Returns:
            (int, dict): eddies earnt, breakdown dict
        """
        minimum = user_dict.daily_minimum

        if minimum is None:
            minimum = self.server_min

        if not user_results and not user_reactions and not user_reacted:
            if minimum == 0:
                return 0, {}

            if minimum < 0:
                if real:
                    self.user_points.set_daily_minimum(user, guild_id, 0)
                return 0, {}

            minimum -= 1
            if real:
                self.user_points.set_daily_minimum(user, guild_id, minimum)
            if minimum == 0:
                return 0, {}
        elif minimum != self.server_min:
            minimum = self.server_min
            if real:
                self.user_points.set_daily_minimum(user, guild_id, minimum)

        message_types = []
        for mess in user_results:
            if isinstance(mess.message_type, list):
                # handle vc later
                if "vc_joined" in mess.message_type or "vc_streaming" in mess.message_type:
                    continue
                message_types.extend(mess.message_type)
            else:
                message_types.append(mess.message_type)

        # REACTION HANDLING
        for message in user_reacted:
            # messages the user sent that got reacted to
            for reaction in message.reactions:
                if reaction.user_id == user:
                    continue
                if start < reaction.timestamp < end:
                    message_types.append("reaction_received")

        for message in user_reactions:
            # messages the user reacted to
            reactions = message.reactions

            our_user_reactions = [
                react for react in reactions if react.user_id == user and (start < react.timestamp < end)
            ]
            for reaction in our_user_reactions:
                if _ := self.server_emojis.get_emoji_from_name(guild_id, reaction.content):
                    message_types.append("custom_emoji_reaction")

                matching_reactions = [
                    react for react in reactions if react.content == reaction.content and react.user_id != user
                ]

                if matching_reactions:
                    # someone else reacted with the same emoji we did
                    _matching = sorted(matching_reactions, key=lambda x: x.timestamp)
                    if _matching[0].timestamp > reaction.timestamp:
                        # we reacted first!
                        message_types.extend("react_train" for _ in matching_reactions)

        for message in user_results:
            # add reaction_received events
            if replies := message.replies:
                for reply in replies:
                    if reply.user_id == user:
                        continue
                    message_types.append("reply_received")
            # add used wordle words
            if wordle_word and wordle_word in message.content:
                message_types.append("wordle_word_used")

        count = Counter(message_types)
        eddies_gained = self._calc_eddies(count, minimum)

        # handle VC stuff here
        # VC events are different as we want to work out eddies on time spent in VC
        vc_joined_events = [vc for vc in user_results if "vc_joined" in vc.message_type]
        vc_total_time = sum([vc.time_in_vc for vc in vc_joined_events])
        vc_eddies = vc_total_time * MESSAGE_VALUES["vc_joined"]

        if vc_total_time:
            # add a minimum of 1 for each VC event
            vc_eddies += len(vc_joined_events)

        eddies_gained += vc_eddies

        vc_streaming_events = [vc for vc in user_results if "vc_streaming" in vc.message_type]
        stream_total_time = sum([vc.time_streaming for vc in vc_streaming_events])
        stream_eddies = stream_total_time * MESSAGE_VALUES["vc_streaming"]

        if stream_total_time:
            # add a minimum of 2 for each streaming event
            stream_eddies += len(vc_streaming_events) * 2

        eddies_gained += stream_eddies

        eddies_gained = math.floor(eddies_gained)

        count["daily"] = minimum

        if vc_total_time:
            count["vc_joined"] = int(vc_total_time)

        if stream_total_time:
            count["vc_streaming"] = int(stream_total_time)

        return eddies_gained, count

    def give_out_eddies(self, guild_id: int, real: bool = False, days: int = 1) -> dict[str, any]:  # noqa: PLR0915, PLR0912, C901
        """Works out all the predicted salary gain for a given server's members.

        Only distributes them if specified.

        Args:
            guild_id (int): The guild ID to process
            real (bool): whether to actually perform operations or not
            days (int): number of days to go back to calc eddies for. Defaults to 1.

        Returns:
            dict: the eddie breakdown for each server member
        """
        start, end = self.get_datetime_objects(days)

        server_min = self.guilds.get_daily_minimum(guild_id)
        if not server_min:
            server_min = 4
        self.server_min = server_min

        # query gets all messages yesterday
        results = self.interactions.query({"guild_id": guild_id, "timestamp": {"$gt": start, "$lt": end}})

        reactions = self.interactions.query({"guild_id": guild_id, "reactions.timestamp": {"$gt": start, "$lt": end}})

        users = self.user_points.get_all_users_for_guild(guild_id)
        users = [u for u in users if not u.inactive]
        user_ids = [u.uid for u in users]
        user_dict = {u.uid: u for u in users}

        eddie_gain_dict = {}
        wordle_messages = []

        try:
            wordle_doc = self.wordles.find_wordles_at_timestamp(start, guild_id)
            wordle_word = wordle_doc.actual_word
        except (AttributeError, IndexError, KeyError):
            wordle_doc = None
            wordle_word = None

        for user in user_ids:
            self.logger.info("processing %s", user)

            user_results = [r for r in results if r.user_id == user]
            user_reacted_messages = [r for r in reactions if r.user_id == user]
            user_reactions = [r for r in reactions if any(react for react in r.reactions if react.user_id == user)]

            eddies_gained, breakdown = self.calc_individual(
                user,
                user_dict[user],
                user_results,
                user_reacted_messages,
                user_reactions,
                start,
                end,
                guild_id,
                wordle_word,
                real,
            )

            try:
                wordle_message = next(w for w in user_results if "wordle" in w.message_type)
                result = re.search(WORDLE_SCORE_REGEX, wordle_message.content).group()
                guesses = result.split("/")[0]

                if guesses != "X":
                    guesses = int(guesses)

                wordle_value = WORDLE_VALUES[guesses]
                eddies_gained += wordle_value

                if "wordle" not in breakdown:
                    breakdown["wordle"] = 3

                breakdown["wordle"] += wordle_value

                if guesses != "X":
                    wordle_messages.append((user, guesses))

            except (IndexError, StopIteration):
                # just means we had an error with this
                pass

            if eddies_gained == 0:
                continue

            eddie_gain_dict[user] = [eddies_gained, breakdown]

        # grab the bot's wordle message here
        results = self.interactions.query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end},
                "user_id": self.bot.user.id,
                "channel_id": GENERAL_CHAT,
                "message_type": "wordle",
            },
        )

        bot_guesses = 100  # arbitrarily high number
        if results:
            bot_message = results[0]
            bot_result = re.search(r"[\dX]/\d", bot_message.content).group()
            bot_guesses = bot_result.split("/")[0]
            bot_guesses = int(bot_guesses) if bot_guesses != "X" else 100

        # do wordle here
        if wordle_messages:
            wordle_messages = sorted(wordle_messages, key=lambda x: x[1])
            top_guess = wordle_messages[0][1]

            if bot_guesses < top_guess:
                top_guess = bot_guesses

            for wordle_attempt in wordle_messages:
                if wordle_attempt[1] == top_guess:
                    gain_dict = eddie_gain_dict[wordle_attempt[0]][1]
                    gain_dict["wordle_win"] = 1
                    eddie_gain_dict[wordle_attempt[0]] = [eddie_gain_dict[wordle_attempt[0]][0] + 5, gain_dict]

        current_king_id = self.user_points.get_current_king(guild_id).uid
        tax_gains = 0

        tax_rate, supporter_tax_rate = self.guilds.get_tax_rate(guild_id)
        self.logger.info("Tax rate is: %s, %s", tax_rate, supporter_tax_rate)

        for _user in eddie_gain_dict:
            if _user == "guild":
                continue

            user_db = self.user_points.find_user(_user, guild_id)
            tr = supporter_tax_rate if user_db.supporter_type == SupporterType.SUPPORTER else tax_rate

            if _user != current_king_id:
                # apply tax
                taxed = math.floor(eddie_gain_dict[_user][0] * tr)
                eddie_gain_dict[_user][0] -= taxed
                eddie_gain_dict[_user].append(taxed)
                tax_gains += taxed

            if real:
                self.logger.info("Incrementing %s by %s", _user, eddie_gain_dict[_user][0])
                self.user_points.increment_points(
                    _user,
                    guild_id,
                    eddie_gain_dict[_user][0],
                    TransactionTypes.DAILY_SALARY,
                )
            self.logger.info("%s gained %s", _user, eddie_gain_dict[_user][0])

        if current_king_id not in eddie_gain_dict:
            # king isn't gaining eddies lol
            eddie_gain_dict[current_king_id] = [0, {}]
        eddie_gain_dict[current_king_id].append(tax_gains)
        eddie_gain_dict[current_king_id][0] += tax_gains

        if real:
            # give king their tax earnings
            self.user_points.increment_points(
                current_king_id,
                guild_id,
                tax_gains,
                TransactionTypes.TAX_GAINS,
            )

        return eddie_gain_dict
