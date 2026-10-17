"""The one file of rn's hooks that reads the repository: it finds the sessions open where an event
comes from and builds each one's record as values, so the checks read no file themselves."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import IO, NamedTuple

from checks import Record, field


class Session(NamedTuple):
    top: str
    folder: str
    record: Record


def read_event(stream: IO[str]) -> dict | None:
    try:
        event = json.load(stream)
    except ValueError:
        return None
    if isinstance(event, dict) and isinstance(event.get("cwd"), str):
        return event
    return None


def git(cwd: str, *args: str) -> str:
    """What git prints, or nothing where git fails or is missing, so a hook outside a session
    stops nothing."""
    try:
        done = subprocess.run(
            ["git", "-C", cwd, *args], capture_output=True, text=True, check=False
        )
    except OSError:
        return ""
    return done.stdout.strip()


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def sessions(top: str) -> list[str]:
    """The session folders the branch changed whose plan is not finished, found as rn's
    references/record.md says. The last fetch stands: the conductor fetches as each session
    starts, and a fetch on every write would wait on the network."""
    base = git(top, "merge-base", "HEAD", "origin/HEAD")
    found = []
    changed = git(top, "diff", "--name-only", base, "HEAD", "--", ".rn/*/steering.md")
    for path in changed.splitlines():
        plan = os.path.join(top, path)
        if os.path.isfile(plan) and field(read(plan), "status") != "finished":
            found.append(os.path.dirname(path))
    return found


def verification_file(top: str, plan: str) -> str | None:
    """None where the plan names no verification document, and `build` gives None where the named
    file is not there yet: the checks read None as a document the Design sign-off has still to
    make, and an empty text as one written broken."""
    name = field(plan, "verification")
    return os.path.join(top, name) if name else None


def build(top: str, folder: str) -> Record:
    plan = read(os.path.join(top, folder, "steering.md"))
    where = os.path.join(top, folder, "open")
    items = (
        {name: read(os.path.join(where, name)) for name in os.listdir(where)}
        if os.path.isdir(where)
        else {}
    )
    verification = verification_file(top, plan)
    return Record(
        folder,
        plan,
        items,
        read(verification) if verification and os.path.isfile(verification) else None,
        field(plan, "rn"),
    )


def open_sessions(event: dict) -> list[Session]:
    top = git(event["cwd"], "rev-parse", "--show-toplevel")
    return [Session(top, folder, build(top, folder)) for folder in sessions(top)] if top else []


def report(found: list[str]) -> None:
    if found:
        sys.stderr.write("".join(sentence + "\n" for sentence in found))
        raise SystemExit(2)
