"""What Lane's unit cases share: the system's temporary folder of each case, where the run record
lies, the folder of `log` with its rules and adapters, and the folder that its conversation works
in, with the files that its steps name."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from typing import Any

import lane_bench
import pytest
from repo_files import write_files


@pytest.fixture(autouse=True)
def temp(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The system's temporary folder of the case, empty."""
    folder = os.path.join(str(tmp_path), "system-temp")
    os.makedirs(folder)
    monkeypatch.setattr(tempfile, "tempdir", folder)
    yield folder


@pytest.fixture
def log(tmp_path: Any) -> str:
    """The folder of `log`, with its rules, its adapters, and its skills."""
    folder = os.path.join(str(tmp_path), "plugins", "log")
    return lane_bench.plugin(
        folder, "log", lane_bench.SKILLS, lane_bench.RULES, lane_bench.ADAPTERS
    )


@pytest.fixture
def cwd(tmp_path: Any) -> str:
    """The folder that the conversation works in, with the notes, a secret, and the entry."""
    folder = os.path.join(str(tmp_path), "repo")
    write_files(
        folder,
        {
            "NOTES.md": lane_bench.NOTES,
            "CHANGELOG.md": lane_bench.ENTRY,
            "secrets/key.txt": "k\n",
        },
    )
    return folder
