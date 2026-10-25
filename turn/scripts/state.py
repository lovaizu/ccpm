"""Where a run stands, kept in `.turn/<yyyymmdd>-<name>/` at the root of the repository, as
dev/architecture.md's Where a plugin writes its files places what a plugin may keep, with each
role's reply beside it, so a call again names the run by its result, on any day, and a run stopped
anywhere goes on from its last move."""

from __future__ import annotations

import glob
import json
import os
import time
from typing import Any

import call

# What marks the root of a repository: a folder, or in a worktree a file, as git and Claude Code's
# plugin check take the nearest folder holding it.
REPOSITORY = ".git"


def root(result: str) -> str:
    """The root of the repository the result is in: the nearest folder at or above the result's
    folder holding REPOSITORY, or the result's folder where none does, as a whole real path."""
    folder = os.path.realpath(os.path.dirname(os.path.abspath(result)))
    up = folder
    while not os.path.exists(os.path.join(up, REPOSITORY)):
        if os.path.dirname(up) == up:
            return folder
        up = os.path.dirname(up)
    return up


def folder(result: str) -> str:
    """The folder the run of the result is kept in, as a whole path: `.turn/<yyyymmdd>-<name>/` at
    the root, the name the result's path from the root, each `%` written `%25` and each folder
    between `%2F`, so two results never share it; the one made on the day the run began, so a run
    gone on with on a later day finds it, or today's where none is made."""
    top = root(result)
    path = os.path.relpath(os.path.realpath(os.path.abspath(result)), top)
    name = "%2F".join(p.replace("%", "%25") for p in path.split(os.sep))
    turn = os.path.join(top, ".turn")
    made = sorted(glob.glob(os.path.join(glob.escape(turn), "[0-9]" * 8 + "-" + glob.escape(name))))
    return made[0] if made else os.path.join(turn, f"{time.strftime('%Y%m%d')}-{name}")


def state_path(result: str) -> str:
    """Where the run is kept: in its folder."""
    return os.path.join(folder(result), "run.json")


def running(result: str) -> dict[str, Any] | None:
    """The run kept for the result at the path, or None when none is."""
    try:
        with open(state_path(result), encoding="utf-8") as f:
            kept = json.load(f)
    except (OSError, ValueError):
        return None
    return kept if isinstance(kept, dict) else None


def going(result: str) -> dict[str, Any]:
    """Goes to the folder the call was made from, where the run's paths mean what they say, and
    gives the run going with its result at the path; stops where none is."""
    run = running(result)
    if run is None:
        raise call.Stop(
            f"turn: no run is going with its result at {result}; start one with"
            " `turn.py start '<call JSON>'`"
        )
    os.chdir(run["root"])
    return run


def save(run: dict[str, Any]) -> None:
    """Keeps where the run stands, in its folder."""
    write(state_path(run["call"]["result"]), run)


def write(path: str, data: dict[str, Any]) -> None:
    """Writes the data as JSON at the path, making its folder where it is not there, one key or
    value to a line, so the calling AI and the user can read it."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
