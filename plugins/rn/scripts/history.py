"""The session's history on its branch since it left the default branch, where the learnings are
looked for once the finished work is approved: each feedback the user sent back with the proposal
that answered it, each work made again and each decision an answer replaced, each with the commit
that kept it and that commit's message, as each move is kept in the commit of its step."""

from __future__ import annotations

import json
from typing import Any

import repo
import session
import steering


def messages(start: str) -> dict[str, str]:
    """The message of each commit on the branch since the start, by the commit, each without the
    blank lines git ends it with."""
    # Each commit as its name and its message, each ended by a NUL, which no message holds.
    listed = repo.git(["log", "--format=%H%x00%B%x00", f"{start}..HEAD"], repo.AS_GIT_SAYS)
    parts = listed.split("\0")
    return {name.strip(): said.strip() for name, said in zip(parts[0::2], parts[1::2])}


def feedback(folder: str, start: str, said: dict[str, str]) -> list[dict[str, Any]]:
    """Each feedback the user sent back at a sign-off, in the order kept: the commit whose steering
    ended the sign-off waiting at the same stage, as feedback does where an approval moves the
    stage, with its message, which holds the feedback whole; and the proposal that answered it, the
    next commit that set the same sign-off waiting, with its message, which shows what changed;
    None where none has yet."""
    path = session.steering_path(folder)
    # Each commit that changed the line setting a sign-off waiting, as only a proposal, setting it
    # where none was, and an answer, ending it, do.
    listed = repo.git(
        ["log", "--reverse", "--format=%H", '-G"awaiting_signoff"', f"{start}..HEAD", "--", path],
        repo.AS_GIT_SAYS,
    ).split()
    found = []
    # Each feedback not yet answered, by the sign-off it was sent back at.
    waiting: dict[str, dict[str, Any]] = {}
    for commit in listed:
        before, now = repo.at(f"{commit}^", path), repo.at(commit, path)
        shown = steering.signoff_of(now)
        if shown in waiting:
            waiting.pop(shown)["answer"] = {"commit": commit, "message": said[commit]}
        ended = steering.signoff_of(before)
        if ended is not None and steering.stage_of(now) == ended:
            sent = {"commit": commit, "signoff": ended, "message": said[commit], "answer": None}
            found.append(sent)
            waiting[ended] = sent
    return found


def remade(folder: str, start: str, said: dict[str, str]) -> list[dict[str, Any]]:
    """Each work made again, in the order made: each call on a work after one of its calls returned
    turn's result, with the commit that added its CCS and that commit's message. A call on the plan
    or the learnings is none, as the orchestrator writes them and turn returns nothing of them, and
    the plan is written again by its own course, as each task's findings change it."""
    returned: set[str] = set()
    found = []
    for made in session.calls(folder, "HEAD"):
        if made.work in returned:
            commit = added(session.call_path(folder, made.number, session.CCS), start)
            found.append(
                {"commit": commit, "work": made.work, "call": made.number, "message": said[commit]}
            )
        # A call on a work no part is made for is closed once turn has returned its result.
        if made.closed and made.work not in session.PARTS:
            returned.add(made.work)
    return found


def added(path: str, start: str) -> str:
    """The commit on the branch since the start that added the file at the path."""
    return repo.git(
        ["log", "--diff-filter=A", "--format=%H", f"{start}..HEAD", "--", path], repo.AS_GIT_SAYS
    ).strip()


def replaced(folder: str, start: str, said: dict[str, str]) -> list[dict[str, Any]]:
    """Each decision an answer replaced, in the order kept, as rn.py decide adds it to the
    session's record, with what it was and is now, and the commit of the step that kept it with
    its message; none for a line that is no JSON object, as only a line written by hand is one."""
    path = session.replaced_path(folder)
    listed = repo.git(
        ["log", "--reverse", "--format=%H", f"{start}..HEAD", "--", path], repo.AS_GIT_SAYS
    ).split()
    found = []
    # The lines the record held before each commit, as each commit adds its own after them.
    held = 0
    for commit in listed:
        lines = (repo.at(commit, path) or "").splitlines()
        for line in lines[held:]:
            try:
                changed = json.loads(line)
            except ValueError:
                continue
            if isinstance(changed, dict):
                found.append({"commit": commit, **changed, "message": said[commit]})
        held = len(lines)
    return found


def history(folder: str) -> dict[str, list[dict[str, Any]]]:
    """The session's history on its branch since it left the default branch: each feedback with
    its answer, each work made again and each decision an answer replaced, as `feedback`, `remade`
    and `replaced` give them; stops where git fails."""
    start = repo.base()
    said = messages(start)
    return {
        "feedback": feedback(folder, start, said),
        "remade": remade(folder, start, said),
        "replaced": replaced(folder, start, said),
    }
