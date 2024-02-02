"""Tests our GitHubAPI class."""

from unittest import mock

from apis.github import GitHubAPI


class TestGitHubAPI:
    """Tests our GitHubAPI class."""

    def test_init(self) -> None:
        """Tests init."""
        api = GitHubAPI("token")
        assert isinstance(api, GitHubAPI)

    def test_raise_issue(self) -> None:
        """Tests raise_issue."""
        api = GitHubAPI("token")
        with mock.patch("requests.post") as _patched:
            api.raise_issue("esloman", "bsebot", "Title", "Some text", "feature")
            assert _patched.call_count == 1

    def test_raise_issue_with_bug(self) -> None:
        """Tests raise_issue."""
        api = GitHubAPI("token")
        with mock.patch("requests.post") as _patched:
            api.raise_issue("esloman", "bsebot", "Title", "Some text", "bug")
            assert _patched.call_count == 1
