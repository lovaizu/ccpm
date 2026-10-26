"""The stretch of the session the learnings are made from: from the last call on the learnings turn
returned, or from where the branch left the default branch; its history on the branch and the
session's files as they are now."""

from __future__ import annotations

import glob
import os
import shlex
import shutil

import conversations
import records
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
    """Each file in the session's folder as it is now, in the order of their paths: the steering,
    the learnings, each research and trial result and each file of its calls to turn."""
    found = glob.glob(os.path.join(glob.escape(folder), "**", "*"), recursive=True)
    return sorted(p for p in found if os.path.isfile(p))


def show(folder: str) -> list[str]:
    """Shows the stretch of the session the learnings are made from: its record, the history on the
    branch since the stretch began and the session's files as they are now; then each conversation
    of the orchestrator, run at the top of the repository on the session's branch, from the time
    the stretch began, none where Claude Code keeps none here, as when the session ran on another
    machine. Each is written as text in the git folder, made afresh, where nothing is committed;
    gives their paths, the record first."""
    start = stretch(folder)
    began = float(repo.git(["log", "-1", "--format=%ct", start], repo.AS_GIT_SAYS))
    place = records_folder()
    shutil.rmtree(place, ignore_errors=True)
    # Each text shown, by where it is written, with its text.
    texts = [(os.path.join("record", "history.txt"), history(folder, start))]
    texts += [(os.path.join("record", p), repo.read_text(p)) for p in session_files(folder)]
    for path in conversations.conversations(repo.top(), repo.branch()):
        name = os.path.basename(path)[: -len(".jsonl")] + ".txt"
        text = conversations.told(path, began)
        if text:
            texts.append((os.path.join("conversations", name), text))
    for name, text in texts:
        repo.write_text(os.path.join(place, name), records.wrapped(text))
    return [os.path.join(place, name) for name, _ in texts]
