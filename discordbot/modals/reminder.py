
import datetime

import discord

import discordbot.utilities
from mongo.bsepoints.reminders import ServerReminders


class ReminderModal(discord.ui.Modal):
    def __init__(self, logger, message_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.logger = logger
        self.server_reminders = ServerReminders()
        self.message_id = message_id

        self.reminder_reason = discord.ui.InputText(
            label="Reminder name/reason",
            placeholder="Remind you about..."
        )

        self.reminder_timeout = discord.ui.InputText(
            label="Timeout: DIGITS + (s|m|h|d|w) (Optional)",
            placeholder=(
                "Examples: 30m, 8h, 1d12h, 12h30m10s, 1w3d2h, etc..."
            )
        )

        self.add_item(self.reminder_reason)
        self.add_item(self.reminder_timeout)

    async def callback(self, interaction: discord.Interaction):
        """

        :param interaction:
        :return:
        """
        await interaction.response.defer(ephemeral=True)

        reason = self.reminder_reason.value
        timeout = self.reminder_timeout.value

        timeout_seconds = discordbot.utilities.convert_time_str(timeout)

        now = datetime.datetime.now()
        timeout_date = now + datetime.timedelta(seconds=timeout_seconds)

        self.logger.info(f"{reason} - {timeout} - {timeout_seconds}")

        reminder_msg = (
            f"{interaction.user.mention} you will be reminded about **{reason}** "
            f"at {timeout_date.strftime('%d %b %y %H:%M')}"
        )

        if not self.message_id:
            reminder_message = await interaction.channel.send(
                content=reminder_msg
            )
        else:
            await interaction.followup.send(content=reminder_msg, ephemeral=True)

        self.server_reminders.insert_reminder(
            interaction.guild.id,
            interaction.user.id,
            now,
            timeout_date,
            reason,
            interaction.channel.id,
            self.message_id or reminder_message.id
        )

        if not self.message_id:
            await interaction.followup.send(content="Reminder set.", ephemeral=True, delete_after=5)
