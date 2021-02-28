import datetime

import discord
from discord.ext import tasks, commands

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from mongo.bsepoints import UserPoints, UserLoans


class BSEddiesLoanCollections(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.user_points = UserPoints()
        self.user_loans = UserLoans()
        self.logger = logger
        self.guilds = guilds
        self.loan_collections.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.loan_collections.cancel()

    @tasks.loop(minutes=5)
    async def loan_collections(self):
        """
        Main collection loop that checks that all the active loans aren't "expired"
        If they are expired - we take the collection amount from the user, update the transaction history and inform
        the user as such
        :return:
        """
        now = datetime.datetime.now()
        for guild in self.guilds:
            active_loans = self.user_loans.get_all_active_loans(guild)
            for active_loan in active_loans:
                timeout = active_loan["due"]
                if now > timeout:
                    # loan has timed out
                    self.logger.info(f"Found {active_loan['loan_id']} that has expired.")
                    amount_due = active_loan["amount_due"]
                    collected_amount = amount_due * 2

                    self.user_points.decrement_points(
                        active_loan["user_id"], guild, collected_amount
                    )

                    self.user_loans.close_loan(
                        guild, active_loan["loan_id"], now
                    )
                    self.user_loans.update(
                        {"loan_id": active_loan["loan_id"], "guild_id": guild},
                        {"$set": {"collected": True}}
                    )

                    self.user_points.append_to_transaction_history(
                        active_loan["user_id"], guild,
                        {
                            "type": TransactionTypes.LOAN_COLLECTION,
                            "amount": collected_amount * -1,
                            "timestamp": now,
                            "loan_id": active_loan["loan_id"],
                            "comment": "New loan taken out",
                        }
                    )

                    self.user_points.append_to_activity_history(
                        active_loan["user_id"], guild,
                        {
                            "type": ActivityTypes.LOAN_COLLECTION,
                            "loan_id": active_loan["loan_id"],
                            "timestamp": now,
                            "comment": f"Collected {collected_amount}"
                        }
                    )

                    self.logger.info(f"Taken {collected_amount} from {active_loan['user_id']} as they failed to pay "
                                     f"back their loan on time {active_loan['load_id']}")

                    user = await self.bot.fetch_user(active_loan["user_id"])
                    message = (f"As you failed to pay back your loan in time - I have taken {collected_amount} out of "
                               f"your account autoamatically.")
                    try:
                        await user.send(content=message)
                    except discord.Forbidden:
                        pass

    @loan_collections.before_loop
    async def before_loan_collections(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
