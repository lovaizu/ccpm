"""Where a run's files are: `.turn/<yyyymmdd>-<name>/` at the root of the repository, as
dev/architecture.md's Where a plugin writes its files places what an agent reads with its tools, the
call kept there with the folder it was made from and each role's last reply beside it, so a call
again finds the run by its result, on any day, and goes on from what the folder holds."""

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
# The file in the run's folder that keeps the call and the folder it was made from.
CALL = "call.json"


def root(result: str) -> str:
    """The root of the repository the result is in: the nearest folder at or above the result's
    folder holding REPOSITORY, or the result's folder where none does, as a whole real path."""
    found = os.path.realpath(os.path.dirname(os.path.abspath(result)))
    up = found
    while not os.path.exists(os.path.join(up, REPOSITORY)):
        if os.path.dirname(up) == up:  # pragma: no mutate
            return found
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


def reply(result: str, role: str) -> str:
    """Where the role of the name, `generator` or `first-user`, writes its last reply, in the run's
    folder."""
    return os.path.join(folder(result), f"{role}.json")


def kept(result: str) -> dict[str, Any] | None:
    """The call kept for the result at the path, with the folder it was made from, or None where no
    run of it is kept."""
    try:
        with open(os.path.join(folder(result), CALL), encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return None


def going(result: str) -> dict[str, Any]:
    """Goes to the folder the call was made from, where the call's paths mean what they say, and
    gives the call of the run going with its result at the path; stops where none is."""
    run = kept(result)
    if run is None:
        raise call.Stop(
            f"turn: no run is going with its result at {result}; start one with"
            " `turn.py start '<call JSON>'`"
        )
    os.chdir(run["root"])
    return run["call"]


def keep(asked: dict[str, Any], made_in: str) -> None:
    """Keeps the call in the run's folder of its result, with the folder it was made from."""
    write(os.path.join(folder(asked["result"]), CALL), {"call": asked, "root": made_in})


def write(path: str, data: dict[str, Any]) -> None:
    """Writes the data as JSON at the path, making its folder where it is not there, one key or
    value to a line, so the calling AI and the user can read it."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
