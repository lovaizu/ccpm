"""What overnight's unit cases share: the stand-in of Claude Code first on the PATH of each case, so
that no case runs the real one, git's identity, and each runner that a case started ended with it;
the person's repository; and a clock in place of the runner's, which moves only as the runner
waits, so that no case waits for a reset, each as `overnight_stand_ins` says."""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any

import overnight_files
import overnight_stand_ins
import pytest
from overnight_stand_ins import Clock


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    """The runner's clock at 23:00 of the walkthrough's night, which moves only as it waits."""
    return overnight_stand_ins.clock_in_place(monkeypatch)


@pytest.fixture(autouse=True)
def stand_in(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The folder of the state of the stand-in of Claude Code, which comes first on the PATH, with
    no plays, so that a run that a case doesn't give fails. Each runner whose run the stand-in made
    has ended once the case ends."""
    state = overnight_stand_ins.stand_in_first(str(tmp_path), monkeypatch)
    yield state
    overnight_stand_ins.end_runners(state)


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The walkthrough's repository `myapp`, on main with its first commit."""
    return overnight_files.repository(os.path.join(str(tmp_path), "work"))
