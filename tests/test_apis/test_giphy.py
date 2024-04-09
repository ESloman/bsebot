"""Tests our GiphyAPI class."""

from unittest import mock

from apis.giphyapi import GiphyAPI


class TestGiphyAPI:
    """Tests our GiphyAPI class."""

    def test_init(self) -> None:
        """Tests init."""
        api = GiphyAPI()
        assert isinstance(api, GiphyAPI)

    async def test_random_gif(self) -> None:
        """Tests random_gif."""
        api = GiphyAPI()
        with mock.patch("aiohttp.ClientSession.get") as _patched:
            await api.random_gif()
            assert _patched.call_count == 1

    async def test_random_gif_with_tag(self) -> None:
        """Tests random_gif."""
        api = GiphyAPI()
        with mock.patch("aiohttp.ClientSession.get") as _patched:
            await api.random_gif("celebrate")
            assert _patched.call_count == 1
