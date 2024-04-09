"""Guphy API class."""

import os

import aiohttp


class GiphyAPI:
    """API Class for interacting with Giphy API."""

    def __init__(self: "GiphyAPI") -> None:
        """Initialise this class.

        Needs a GIPHY API Token/

        Args:
            token (str): the token
        """
        self.token: str | None = os.environ.get("GIPHY_TOKEN")
        self.api_path = "https://api.giphy.com/v1/"

    async def random_gif(self, tag: str | None = None) -> str:
        """Generates a random gif with the given tag.

        Args:
            tag (str, optional): the tag to search for. Defaults to None.

        Returns:
            str: the link to the gif
        """
        url = self.api_path + "gifs/random"

        params = {"api_key": self.token}

        if tag:
            params["tag"] = tag

        async with aiohttp.ClientSession() as session, session.get(url, params=params) as response:
            ret = await response.json()
        return ret["data"]["images"]["original_still"]["url"]
