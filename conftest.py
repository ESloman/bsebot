"""Pytest configuration and globalfixtures."""

import pathlib
import zipfile

import pytest


def pytest_sessionstart(session: pytest.Session) -> None:  # noqa: ARG001
    """Session start hook.

    Called after the Session object has been created and
    before performing collection and entering the run test loop.

    Args:
        _ (Session): the session
    """
    root = pathlib.Path(__file__).parent
    path = pathlib.Path(root, "tests", "mocks", "mock_data", "bestsummereverpoints")
    zip_path = pathlib.Path(path, "testdata.zip")

    json_files = [file for file in zip_path.glob(".json") if not file.startswith("og_")]
    if len(json_files) > 1:
        # we have test data
        return

    # otherwise we need to unpack them
    with zipfile.ZipFile(zip_path, mode="r", compression=zipfile.ZIP_BZIP2) as arch:
        for file in arch.namelist():
            arch.extract(file, path)
