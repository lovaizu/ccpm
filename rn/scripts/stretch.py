"""The stretch of the session the learnings are made from: from the last call on the learnings turn
returned, or from where the branch left the default branch; its history on the branch and the
session's files as they are now; and the learnings turn returned with each call, from every
version of every result."""

from __future__ import annotations

import glob
import json
import os
import shlex
from typing import Any

import repo
import session
import steering

# The folder in the repository's git folder where the records the learnings are made from are shown,
# so nothing of it shows as a change to keep.
RECORDS = "rn"


def records_folder() -> str:
    """The folder where the records the learnings are made from are shown, in the repository's git
    folder, as a whole path."""
    return os.path.join(
        repo.git(["rev-parse", "--absolute-git-dir"], repo.AS_GIT_SAYS).strip(), RECORDS
    )


def stretch(folder: str) -> str:
    """The commit the stretch the learnings are made from starts after: the one that kept the
    result of the last call on the learnings turn returned, or, where none is, the one the branch
    left the default branch at."""
    done = [c for c in session.calls(folder) if c.work == steering.LEARNINGS and c.result]
    if not done:
        return repo.base()
    result = session.call_path(folder, done[-1].number, session.RESULT)
    return repo.git(["log", "-1", "--format=%H", "--", result], repo.AS_GIT_SAYS).strip()


def history(folder: str, start: str) -> str:
    """The session's history on the branch since the start, each command before what it printed:
    each commit, oldest first, with its message, which holds each feedback, answer and proposal
    shown, and the files it changed, so a change to the work made outside turn shows, without their
    lines, as the record gives the session's files as they are now; then each change to the
    steering, under the commit that made it, which shows what each move rested on."""
    asked = [
        ["log", "--reverse", "--stat", f"{start}..HEAD"],
        [
            "log",
            "--reverse",
            "-p",
            "--format=%h",
            f"{start}..HEAD",
            "--",
            session.steering_path(folder),
        ],
    ]
    return "".join(f"$ {shlex.join(['git', *a])}\n{repo.git(a, repo.AS_GIT_SAYS)}\n" for a in asked)


def session_files(folder: str) -> list[str]:
    """The session's files as they are now: the steering, the learnings, and each file of its calls
    to turn."""
    found = [session.steering_path(folder), session.learnings_path(folder)]
    found += sorted(glob.glob(os.path.join(glob.escape(folder), session.TURN, "*")))
    return [p for p in found if os.path.isfile(p)]


def turns_learnings(folder: str) -> list[dict[str, Any]]:
    """Each learning turn returned for a work of the session, from every version of every result
    committed on the branch since it left the default branch, as a work made again leaves the one
    before in the history alone; oldest first, each once, with the work, the call and the commit
    that first held it. A version that is no JSON object is passed over, as no result of turn's;
    turn's result names its learnings `lessons`."""
    works = {c.number: c.work for c in session.calls(folder)}
    listed = repo.git(
        [
            "log",
            "--reverse",
            "--format=commit %H",
            "--name-only",
            "--diff-filter=AM",
            f"{repo.base()}..HEAD",
            "--",
            os.path.join(folder, session.TURN, f"*-{session.RESULT}"),
        ],
        repo.AS_GIT_SAYS,
    )
    found: list[dict[str, Any]] = []
    seen: list[dict[str, Any]] = []
    commit = ""
    for line in listed.splitlines():
        if line.startswith("commit "):
            commit = line[len("commit ") :]
        file = session.CALL.fullmatch(os.path.basename(line))
        if file is None:
            continue
        try:
            data = json.loads(repo.git(["show", f"{commit}:{line}"], repo.AS_GIT_SAYS))
        except ValueError:
            continue
        for learnt in data.get("lessons", []) if isinstance(data, dict) else []:
            if learnt not in seen:
                seen.append(learnt)
                found.append(dict(learnt, work=works.get(file[1], ""), call=file[1], commit=commit))
    return found
