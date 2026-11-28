"""Where a work's state and log lie, and the form of each: the folder that the start prints, which
holds state.json and the work's one log, as overnight's README says."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime

# Where the user's tools keep their state, as the XDG Base Directory Specification's default of
# $XDG_STATE_HOME says, apart from the folder that the work runs in.
_STATES = os.path.join("~", ".local", "state", "overnight")
STATE = "state.json"
LOG = "log"


@dataclass(frozen=True)
class State:
    """A work's state: its `status`, `running`, `done`, or `failed`; the `dir` it runs in; the
    `session_id` of its conversation, or None before a run names one; and how many `runs` it has
    had."""

    status: str
    dir: str
    session_id: str | None
    runs: int


def start(now: datetime, folder: str) -> str:
    """Makes the folder of a new work that starts at `now` and runs in `folder`, named
    ~/.local/state/overnight/<yyyymmdd-hhmmss>, with its state running with no runs, and gives its
    path. A work that starts in the same second as others takes the name with the next number from
    2, such as <yyyymmdd-hhmmss>-2."""
    states = os.path.expanduser(_STATES)
    os.makedirs(states, exist_ok=True)
    name = now.strftime("%Y%m%d-%H%M%S")
    work = os.path.join(states, name)
    number = 1
    while True:
        try:
            os.mkdir(work)
            break
        except FileExistsError:
            number += 1
            work = os.path.join(states, f"{name}-{number}")
    write(work, State("running", folder, None, 0))
    return work


def write(work: str, state: State) -> None:
    """Has the state.json of the work in the folder `work` hold `state` alone. A reader at any
    moment finds the old state or the new, never part of one."""
    path = os.path.join(work, STATE)
    with open(path + ".new", "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, indent=2)
        f.write("\n")
    os.replace(path + ".new", path)


def log(work: str, line: str) -> None:
    """Adds `line` and a newline at the end of the log of the work in the folder `work`."""
    with open(os.path.join(work, LOG), "a", encoding="utf-8") as f:
        f.write(line + "\n")
