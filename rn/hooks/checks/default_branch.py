"""rn's guard of the session's own branch: a `git commit` or `git push` while the default branch is
checked out, or a `git push` whose destination is the default branch, is stopped, so that the work
goes on the session's branch and reaches the default branch only when the user merges its pull
request.

A session is one piece of rn's work from `/rn:up` to the merge, kept in a folder
`.rn/<yyyymmdd>-<slug>/` on a branch of its own, the session's branch; the default branch is the
remote's, as git knows it from `origin/HEAD`. The guard acts only where the work is rn's: on the
default branch, where a session's folder is in the repository; on any other branch, where that
branch holds a session, as `rn.py session` finds it. Elsewhere every command goes on.

It reads the command statement by statement through shell.py, the hooks' reading of a command the
plugins share, and judges each statement whose first words are `git commit` or `git push`, in the
folder the tool call runs in.
"""

from __future__ import annotations

import os
from typing import Any

import shell

import rn

# The first words of the statements the guard judges, those that keep work in git.
KEEPS = (["git", "commit"], ["git", "push"])
# The options of `git push` that take the next word as their value.
PUSH_VALUED = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}


def git(args: list[str]) -> str | None:
    """What git prints for the arguments in the folder the hook runs in, without the line's end;
    None where git fails, such as outside a repository or on a detached HEAD."""
    try:
        return rn.git(args, "").strip()
    except rn.Stop:
        return None


def sessions_kept(top: str) -> bool:
    """Whether a session's folder, `.rn/<yyyymmdd>-<slug>/`, is in the repository at the top."""
    record = os.path.join(top, rn.RECORD)
    return os.path.isdir(record) and any(
        rn.SESSION_NAME.fullmatch(name) and os.path.isdir(os.path.join(record, name))
        for name in os.listdir(record)
    )


def destination(refspec: str, branch: str | None) -> str | None:
    """The branch a refspec of `git push` sends to: what follows its `:`, or the refspec itself
    where it has none, `HEAD` being the checked-out branch, None where HEAD is detached."""
    source, colon, target = refspec.lstrip("+").partition(":")
    name = target if colon else source
    if name == "HEAD":
        return branch
    return name.removeprefix("refs/heads/")


def destinations(args: list[str], branch: str | None) -> list[str | None]:
    """The branches `git push` with the arguments sends to: each refspec's, after the repository;
    where none is given, where git pushes the checked-out branch, none where git knows no such
    place."""
    plain = []
    rest = iter(args)
    for word in rest:
        if word in PUSH_VALUED:
            next(rest, None)
        elif not word.startswith("-"):
            plain.append(word)
    if plain[1:]:
        return [destination(refspec, branch) for refspec in plain[1:]]
    pushed = git(["rev-parse", "--abbrev-ref", "@{push}"])
    return [pushed.partition("/")[2]] if pushed else []


def stops(keeps: list[list[str]]) -> list[str]:
    """What to say of the first of the statements that commits or pushes on the default branch, or
    pushes to it from a branch holding a session; nothing where none does. Run from the top of the
    repository, as rn.py's functions are."""
    default = rn.default_branch().partition("/")[2]
    branch = git(["symbolic-ref", "--short", "-q", "HEAD"])
    why = f"rn keeps every change on the session's own branch, so that it reaches {default} only"
    why += " when the user merges the pull request"
    for statement in keeps:
        named = " ".join(statement[:2])
        if branch == default:
            stop = (
                f"`{named}` runs on {default}, the default branch, which is checked out; switch to"
                " the session's branch with `git switch <branch>`, or make one with `git switch -c"
                f" <slug>`, and run it there: {why}"
            )
            return [stop]
        # Written as membership rather than `==`, since an order comparison such as `>=` would also
        # tell "push" from "commit", and a mutant making it one would pass every test.
        pushed = statement[1] in ("push",) and default in destinations(statement[2:], branch)
        if pushed and rn.session() is not None:
            own = branch or "HEAD:<the session's branch>"
            stop = (
                f"`{named}` sends to {default}, the default branch; push the session's branch to"
                f" its own name instead, as `git push origin {own}`: {why}"
            )
            return [stop]
    return []


def check(event: dict[str, Any]) -> list[str]:
    """What to say to stop the tool call of the PreToolUse event, as `stops` gives it, or what
    rn.py says where it cannot find the default branch or the session; nothing where the call is
    no `git commit` or `git push`, or the work is not rn's. Leaves the hook in the folder it was
    in."""
    # Written as membership rather than `!=`, since an order comparison such as `>` would also tell
    # "Write" from "Bash", and a mutant making it one would pass every test.
    if event["tool_name"] not in ("Bash",):
        return []
    command = str(event["tool_input"].get("command", ""))
    said = [shell.without_redirects(w) for _, w, _ in shell.statements(command, event["cwd"])]
    keeps = [statement for statement in said if statement[:2] in KEEPS]
    top = git(["rev-parse", "--show-toplevel"]) if keeps else None
    if top is None or not sessions_kept(top):
        return []
    here = os.getcwd()
    os.chdir(top)
    try:
        return stops(keeps)
    except rn.Stop as stop:
        return [str(stop).removeprefix("rn: ")]
    finally:
        os.chdir(here)
