"""Github API class."""

import requests


class GitHubAPI:
    """Class for interactino with Github API."""

    def __init__(self: "GitHubAPI", token: str) -> None:
        """Initialisation method.

        Args:
            token (str): the API token
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def raise_issue(self: "GitHubAPI", owner: str, repo: str, title: str, body: str, _type: str) -> requests.Response:
        """Raises an issue in the specified repo.

        Args:
            owner (str): the owner of the repo
            repo (str): the repo
            title (str): issue title
            body (str): issue body
            _type (str): issue type; either 'bug' or 'feature'

        Returns:
            bool: whether the issue was created or not
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"

        labels = ["enhancement", "suggested"]

        if _type == "bug":
            labels.append("bug")
        else:
            labels.append("newfeature")

        body = f"**[RAISED VIA APPLICATION COMMAND]**\n\n{body}"

        data = {"title": title, "body": body, "labels": labels}

        return requests.post(url, headers=self.headers, json=data, timeout=10)

    def get_releases(self: "GitHubAPI", owner: str, repo: str) -> requests.Response:
        """Gets the releases for a given repo.

        Args:
            owner (str): _description_
            repo (str): _description_

        Returns:
            requests.Response: _description_
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/releases"
        return requests.get(url, headers=self.headers, timeout=10)

    def get_latest_release(self: "GitHubAPI", owner: str, repo: str) -> requests.Response:
        """Gets the latest releases for a given repo.

        Args:
            owner (str): _description_
            repo (str): _description_

        Returns:
            requests.Response: _description_
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/releases/latest"
        return requests.get(url, headers=self.headers, timeout=10)
