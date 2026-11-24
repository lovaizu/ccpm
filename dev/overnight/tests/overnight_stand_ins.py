"""What overnight's unit and property-based cases put in place of what lies outside the part they
call: the stand-in of Claude Code first on the PATH, so that no case runs the real one, with git's
identity, and each runner whose run it made ended once the case ends; what hand-over leaves for a
runner, the piece's folder and its record; and a clock in place of the runner's, which moves only
as the runner waits, so that no case waits for a reset.

The clock takes the place of `runner.clock`'s `now` and `wait_until` by giving each function the
body of the clock's, so that each caller meets it, however it imports them."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import overnight_files
import pytest
from claude_code import claude_double
from overnight_files import PROMPT, TOOLS
from pieces.record import Handed, begin
from runner import clock as runner_clock
from runner.carry import Piece

# The zone of the clock in place of the runner's, east of UTC, so that a time read in UTC, or a
# time with no zone, gives another result.
ZONE = timezone(timedelta(hours=9))
# The time the clock reads as a case starts: 23:00 of the walkthrough's night, a Tuesday.
NIGHT = datetime(2026, 11, 24, 23, 0, tzinfo=ZONE)
# The walkthrough's stop of the usage limit at 01:12, and its reset at 04:00, in the clock's zone.
STOP = datetime(2026, 11, 25, 1, 12, tzinfo=ZONE)
RESET = datetime(2026, 11, 25, 4, 0, tzinfo=ZONE)


@dataclass
class Clock:
    """The clock in place of the runner's: the time it reads, and each time waited until."""

    at: datetime
    waits: list[datetime] = field(default_factory=list)


# The clock that the bodies below read, set in runner.clock's own globals while a case runs.
_held = Clock(NIGHT)


def _now() -> datetime:
    return _held.at


def _wait_until(when: datetime) -> None:
    _held.waits.append(when)
    _held.at = max(_held.at, when)


def clock_in_place(monkeypatch: pytest.MonkeyPatch) -> Clock:
    """Puts the clock in place of the runner's, at 23:00 of the walkthrough's night, and gives
    it."""
    held = Clock(NIGHT)
    monkeypatch.setattr(runner_clock, "_held", held, raising=False)
    monkeypatch.setattr(runner_clock.now, "__code__", _now.__code__)
    monkeypatch.setattr(runner_clock.wait_until, "__code__", _wait_until.__code__)
    return held


def stand_in_first(folder: str, monkeypatch: pytest.MonkeyPatch) -> str:
    """Puts the stand-in of Claude Code first on the PATH, its state in `<folder>/claude` with no
    plays, so that a run that a case doesn't give fails, and git's identity in the environment;
    and gives the folder of its state."""
    state = os.path.join(folder, "claude")
    bin_folder = claude_double.program(os.path.join(folder, "bin"), state)
    claude_double.plays(state, {})
    monkeypatch.setenv("PATH", os.pathsep.join([bin_folder, os.environ.get("PATH", "")]))
    for name, value in overnight_files.IDENTITY.items():
        monkeypatch.setenv(name, value)
    return state


def end_runners(state: str) -> None:
    """Releases each hold of the stand-in, and waits until each runner whose run it made has ended,
    ending each that hasn't."""
    with open(os.path.join(state, claude_double.RELEASE_ALL), "w", encoding="utf-8"):
        pass
    runners = {each["ppid"] for each in claude_double.calls(state)} - {os.getpid()}
    try:
        overnight_files.until(lambda: not any(map(overnight_files.alive, runners)))
    except AssertionError:
        for pid in runners:
            overnight_files.kill(pid)


def handed_over(
    repo: str, prompt: str = PROMPT, tools: tuple[str, ...] = TOOLS
) -> tuple[Piece, Handed]:
    """Puts in place what hand-over leaves for the runner of piece 1 with the prompt and tools: its
    folder made beside the repository, and its record running, carried by this process; and gives
    the piece as its runner carries it, and the piece handed over."""
    folder = overnight_files.piece_folder(repo, 1)
    os.makedirs(folder)
    handed = overnight_files.handed(1, tools)
    begin(repo, handed, os.getpid())
    return Piece(repo, 1, folder, prompt, tools), handed


def path_without_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sets the PATH that `overnight_files.path_without_claude` gives."""
    monkeypatch.setenv("PATH", overnight_files.path_without_claude())
