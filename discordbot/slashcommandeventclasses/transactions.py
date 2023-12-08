"""Transactions slash command."""

import contextlib
import logging
import os

import discord
import xlsxwriter

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class TransactionHistory(BSEddies):
    """Class for handling `/bseddies transactions` command."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.activity_type = ActivityTypes.BSEDDIES_TRANSACTIONS
        self.help_string = "View your recent transactions"
        self.command_name = "transactions"

    @staticmethod
    async def _handle_recent_trans(ctx: discord.ApplicationContext, transaction_history: list) -> None:
        """This handles our 'recent transaction history' command.

        We take the last ten items in the transaction history and
        build a nice formatted ephemeral message with it and send it to the user.

        Args:
            ctx (discord.ApplicationContext): _description_
            transaction_history (list): _description_
        """
        recent_history = transaction_history[-10:]

        message = "This is your recent transaction history.\n"

        for item in recent_history:
            message += (
                f"\n"
                f"**Timestamp**: {item['timestamp'].strftime('%d %b %y %H:%M:%S')}\n"
                f"**Transaction Type**: {TransactionTypes(item['type']).name}\n"
                f"**Change amount**: {item['amount']}\n"
                f"**Running eddies total**: {item['points']}\n"
                f"**Comment**: {item.get('comment', 'No comment')}\n"
            )

            if b_id := item.get("bet_id"):
                message += f"**Bet ID**: {b_id}\n"

            if l_id := item.get("loan_id"):
                message += f"**Loan ID**: {l_id}\n"

            if u_id := item.get("user_id"):
                message += f"**User ID**: {u_id}\n"

        await ctx.respond(content=message, ephemeral=True)

    @staticmethod
    async def _handle_full_trans(ctx: discord.ApplicationContext, transaction_history: list) -> None:
        """Method for handling out "full transaction history" command.

        This mostly just builds an XLSX file that we can send to the user. We use the XLSXWRITER library to do the
        heavy lifting here.

        Once we've created the file, we send it to the user in a DM and send an ephemeral message to let the user know.
        Ephemeral messages don't support file attachments yet.
        :param ctx:
        :param transaction_history:
        :return:
        """
        path = os.path.join(os.path.expanduser("~"), "trans_files")
        f_name = f"full_trans_{ctx.author.id}.xlsx"

        if not os.path.exists(path):
            os.makedirs(path)

        full_name = os.path.join(path, f_name)

        workbook = xlsxwriter.Workbook(full_name)
        worksheet = workbook.add_worksheet("Transaction History")

        cols = ["Item", "Type", "Timestamp", "Change amount", "Eddies", "Bet ID", "Loan ID", "User ID", "Comment"]
        worksheet.write_row(0, 0, cols, workbook.add_format({"bold": True}))

        row = 1
        for item in transaction_history:
            worksheet.write_row(
                row,
                0,
                [
                    row,
                    TransactionTypes(item["type"]).name,
                    item["timestamp"].strftime("%d %b %y %H:%M:%S"),
                    item["amount"],
                    item["points"],
                    item.get("bet_id", "N/A"),
                    item.get("loan_id", "N/A"),
                    item.get("user_id", "N/A"),
                    item.get("comment", "No comment"),
                ],
            )
            row += 1

        center_format = workbook.add_format()
        center_format.set_align("center")
        center_format.set_align("vcenter")

        worksheet.set_column("A:A", cell_format=center_format)
        worksheet.set_column("B:B", width=18)
        worksheet.set_column("C:D", width=20)
        worksheet.set_column("I:I", width=50)

        workbook.close()

        with contextlib.suppress(discord.Forbidden):
            await ctx.author.send(
                content="Here's your full transaction history:",
                file=discord.File(full_name, f_name),
                silent=True,
            )

        await ctx.respond(content="I've sent you a DM with your full history.", ephemeral=True)

    async def transaction_history(self, ctx: discord.ApplicationContext, full: str | None) -> None:
        """Gets the user history and takes the last 10 entries and then displays that list to the user.

        Args:
            ctx (discord.ApplicationContext): the context
            full (str | None): whether to do full stats or not
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(
            ctx.author,
            ctx.guild_id,
            ActivityTypes.BSEDDIES_TRANSACTIONS,
            full=full,
        )

        user = self.user_points.find_user(ctx.author.id, ctx.guild.id)
        transaction_history = user["transaction_history"]

        amount = 0
        for item in transaction_history:
            if transaction_history.index(item) == 0:
                item["points"] = item["amount"]
                amount = item["amount"]
                continue
            amount += item["amount"]
            item["points"] = amount

        if full is None:
            await self._handle_recent_trans(ctx, transaction_history)
        else:
            await self._handle_full_trans(ctx, transaction_history)
