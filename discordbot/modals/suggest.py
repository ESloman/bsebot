
import discord

from apis.github import GitHubAPI


class SuggestModal(discord.ui.Modal):
    def __init__(self, logger, github_api: GitHubAPI, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.logger = logger
        self.github = github_api

        self.add_item(discord.ui.InputText(label="Issue title", placeholder="Enter a summary of your issue"))
        self.add_item(
            discord.ui.InputText(
                label="Issue description",
                placeholder="Please enter a description of the issue/improvement.",
                style=discord.InputTextStyle.long
            )
        )

    async def callback(self, interaction: discord.Interaction):
        """

        :param interaction:
        :return:
        """
        await interaction.response.defer(ephemeral=True)

        response_components = interaction.data["components"]
        issue_title_comp = response_components[0]
        issue_title = issue_title_comp["components"][0]["value"]

        issue_body_comp = response_components[1]
        issue_body = issue_body_comp["components"][0]["value"]

        issue_body = f"Created by: `{interaction.user.name}`.\n\n{issue_body}"

        ret = self.github.raise_issue(
            "ESloman",
            "bsebot",
            issue_title,
            issue_body,
            "feature"
        )

        if ret.status_code != 201:
            # something went wrong
            await interaction.followup.send(
                content=f"Something went wrong raising an issue: `{ret.json()}`",
                ephemeral=True
            )
            return

        msg = f"Created an issue for you. Link: {ret.json()['url'].replace('api.', '').replace('repos/', '')}"
        await interaction.followup.send(
            content=msg,
            ephemeral=True
        )
