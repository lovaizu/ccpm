"""What overnight's unit cases share: the stand-in of Claude Code first on the PATH of each case, so
that no case runs the real one, git's identity, and each runner that a case started ended with it;
the person's repository; and a clock in place of the runner's, which moves only as the runner
waits, so that no case waits for a reset.

The clock takes the place of `runner.clock`'s `now` and `wait_until` by giving each function the
body of the clock's, so that each caller meets it, however it imports them."""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import overnight_files
import pytest
from claude_code import claude_double
from runner import clock as runner_clock

# The zone of the clock in place of the runner's, east of UTC, so that a time read in UTC, or a
# time with no zone, gives another result.
ZONE = timezone(timedelta(hours=9))
# The time the clock reads as a case starts: 23:00 of the walkthrough's night, a Tuesday.
NIGHT = datetime(2026, 11, 24, 23, 0, tzinfo=ZONE)


@dataclass
class Clock:
    """The clock in place of the runner's: the time it reads, and each time waited until."""

    at: datetime
    waits: list[datetime] = field(default_factory=list)


# The clock that the bodies below read, set in runner.clock's own globals while a case runs.
_held: Clock


def _now() -> datetime:
    return _held.at


def _wait_until(when: datetime) -> None:
    _held.waits.append(when)
    _held.at = max(_held.at, when)


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    """The runner's clock at 23:00 of the walkthrough's night, which moves only as it waits."""
    held = Clock(NIGHT)
    monkeypatch.setattr(runner_clock, "_held", held, raising=False)
    monkeypatch.setattr(runner_clock.now, "__code__", _now.__code__)
    monkeypatch.setattr(runner_clock.wait_until, "__code__", _wait_until.__code__)
    return held


@pytest.fixture(autouse=True)
def stand_in(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The folder of the state of the stand-in of Claude Code, which comes first on the PATH, with
    no plays, so that a run that a case doesn't give fails. Each runner whose run the stand-in made
    has ended once the case ends."""
    state = os.path.join(str(tmp_path), "claude")
    bin_folder = claude_double.program(os.path.join(str(tmp_path), "bin"), state)
    claude_double.plays(state, {})
    monkeypatch.setenv("PATH", os.pathsep.join([bin_folder, os.environ.get("PATH", "")]))
    for name, value in overnight_files.IDENTITY.items():
        monkeypatch.setenv(name, value)
    yield state
    with open(os.path.join(state, claude_double.RELEASE_ALL), "w", encoding="utf-8"):
        pass
    runners = {each["ppid"] for each in claude_double.calls(state)} - {os.getpid()}
    try:
        overnight_files.until(lambda: not any(map(overnight_files.alive, runners)))
    except AssertionError:
        for pid in runners:
            overnight_files.kill(pid)


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The walkthrough's repository `myapp`, on main with its first commit."""
    return overnight_files.repository(os.path.join(str(tmp_path), "work"))
