import aiohttp


class GiphyAPI(object):
    """
    API Class for interacting with Giphy API
    """
    def __init__(self, token):
        """
        Constructor this class. Needs a GIPHY API Token
        :param token:
        """
        self.token = token
        self.api_path = "https://api.giphy.com/v1/"

    async def random_gif(self, tag: str = None) -> str:
        url = self.api_path + "gifs/random"

        params = {"api_key": self.token}

        if tag:
            params["tag"] = tag

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                ret = await response.json()
        return ret["data"]["images"]["original_still"]["url"]
