"""The one file of rn's hooks that reads the repository: it finds the open session as
references/record.md gives, builds its record for the checks, and reports their stops."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import NoReturn

from checks import (
    Record,
    front_matter,
    open_names,
    steering_form,
    trace,
    verification_path,
    version,
)

PLANS = ".rn/*/steering.md"


def event(text: str) -> dict:
    """The event Claude Code hands the hook; one that is not a JSON object is read as empty, so that
    nothing is stopped on it."""
    try:
        data = json.loads(text)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def records(data: dict) -> list[Record]:
    """A repository without `.rn/` is left before git is asked about its remote, so that rn changes
    nothing in a repository it is not used in."""
    cwd = data.get("cwd")
    top = git(cwd, "rev-parse", "--show-toplevel").strip() if isinstance(cwd, str) else ""
    if not top or not os.path.isdir(os.path.join(top, ".rn")):
        return []
    found = [build(top, session) for session in sessions(top)]
    return [rec for rec in found if rec is not None]


def sessions(top: str) -> list[str]:
    """A plan written but not yet committed counts as changed, since the write hook checks the plan
    the conductor has just written."""
    base = git(top, "merge-base", "HEAD", "origin/HEAD").strip()
    if not base:
        git(top, "remote", "set-head", "origin", "--auto")
        base = git(top, "merge-base", "HEAD", "origin/HEAD").strip()
    if not base:
        return []
    changed = git(top, "diff", "--name-only", base, "--", PLANS) + git(
        top, "ls-files", "--others", "--exclude-standard", "--", PLANS
    )
    return sorted({os.path.dirname(path) for path in changed.split()})


def build(top: str, session: str) -> Record | None:
    """The session's record, or None when its plan is gone, finished, or from before rn 0.9, whose
    record /rn:up brings to the current form."""
    plan = read(os.path.join(top, session, "steering.md"))
    fields = front_matter(plan or "") or {}
    if plan is None or fields.get("status") == "finished" or version(fields.get("rn", "")) < (0, 9):
        return None
    folder = os.path.join(top, session, "open")
    texts = {
        name: read(os.path.join(folder, name))
        for name in (os.listdir(folder) if os.path.isdir(folder) else [])
    }
    items = {name: text for name, text in texts.items() if text is not None}
    return Record(
        session, plan, items, read(os.path.join(top, verification_path(plan))), fields["rn"], top
    )


def form(rec: Record) -> list[str]:
    """Both entry files and the fixtures test run the form checks from here, so that which checks
    the record's form is held to is changed in one place."""
    return [
        sentence for check in (steering_form, open_names, trace) for sentence in check.check(rec)
    ]


def written(data: dict, rec: Record) -> bool:
    """A path given relative is read from the event's `cwd`, so that a write is matched to the
    record however its path is given."""
    path = (data.get("tool_input") or {}).get("file_path")
    if not isinstance(path, str):
        return False
    rel = os.path.relpath(
        os.path.realpath(os.path.join(data["cwd"], path)), os.path.realpath(rec.top)
    )
    rel = rel.replace(os.sep, "/")
    return (
        rel == f"{rec.session}/steering.md"
        or rel.startswith(f"{rec.session}/open/")
        or rel == os.path.normpath(verification_path(rec.plan))
    )


def report(problems: list[str]) -> NoReturn:
    """Exit 2 is the code on which Claude Code hands standard error to the AI, so that the conductor
    reads each stop and mends the record."""
    sys.stderr.write("".join(f"{problem}\n" for problem in problems))
    sys.exit(2 if problems else 0)


def git(cwd: str, *args: str) -> str:
    """A git that fails or cannot be run prints nothing here, so a repository rn cannot read is
    taken as one with no open session: a hook must not stop work it cannot tell is rn's."""
    try:
        done = subprocess.run(
            ["git", "-C", cwd, *args], capture_output=True, text=True, check=False
        )
    except OSError:
        return ""
    return done.stdout


def read(path: str) -> str | None:
    """None for what cannot be read as a file, such as a folder inside open/; bytes not in UTF-8 are
    replaced, so that one broken byte does not keep the rest of the record from being checked."""
    try:
        with open(path, encoding="utf-8", errors="replace") as file:
            return file.read()
    except OSError:
        return None
