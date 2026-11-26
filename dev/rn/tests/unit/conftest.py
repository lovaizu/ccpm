"""What rn's unit cases share: the system's temporary folder of each case, empty; a host that runs
git for real and gh from its records, with its state in the case's own folder; and a clock in place
of the one by which rn waits for a pull request's CI, which moves only as rn sleeps, so that no case
waits."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from typing import Any

import pytest
from gh import gh_double
from repository import push


@pytest.fixture(autouse=True)
def temp(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The system's temporary folder of the case, empty."""
    folder = os.path.join(str(tmp_path), "system-temp")
    os.makedirs(folder)
    monkeypatch.setattr(tempfile, "tempdir", folder)
    yield folder


@pytest.fixture
def gh_state(tmp_path: Any) -> str:
    """The folder of the double of gh's state."""
    return os.path.join(str(tmp_path), "gh")


@pytest.fixture
def host(gh_state: str) -> Any:
    """A host that runs git for real and gh from its records, keeping each command it ran in its
    `ran`."""
    return gh_double.host(gh_state)


class Clock:
    """A clock in place of push's, whose sleep moves it on by the seconds asked, each kept."""

    def __init__(self) -> None:
        self.now = 1000.0
        self.slept: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


@pytest.fixture(autouse=True)
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    """push's clock, which moves only as rn sleeps, so that a wait of minutes takes none."""
    held = Clock()
    monkeypatch.setattr(push.time, "monotonic", held.monotonic)
    monkeypatch.setattr(push.time, "sleep", held.sleep)
    return held
