"""Where a run stands, kept in a file beside its result, so a call again names the run by its
result, and a run stopped anywhere goes on from its last move."""

from __future__ import annotations

import json
import os
from typing import Any

import call


def state_path(result: str) -> str:
    """Where the run is kept: beside its result."""
    return result + ".run.json"


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
    """Keeps where the run stands, beside its result."""
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
