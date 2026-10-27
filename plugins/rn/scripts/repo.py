"""What rn runs and keeps in the user's repository: git and GitHub's command, each failure a stop
with what they said; the files it writes, which a fresh conversation goes on from; the message of
each move written within a step, held for the commit the step ends with; and what is committed,
pushed, as another machine goes on from what is pushed alone."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

import stop

# What a stop whose git command failed says to do where only git's own words tell what is wrong.
AS_GIT_SAYS = "fix it as git says, then run this again"
# The file in git's own folder for the repository that holds the message of each move written
# since the last commit, each ended by a NUL, which no message holds: git keeps it beside the
# working tree, out of what is committed, for the commit the step ends with.
HELD = "rn-messages"


def ran(command: list[str], failed: str, fed: str | None = None) -> str:
    """What the command prints, with the text fed to its input; stops with what it said and the
    action given, or where it cannot be run, saying to install it."""
    try:
        done = subprocess.run(command, check=False, capture_output=True, text=True, input=fed)
    except OSError as why:
        raise stop.Stop(
            f"rn: {command[0]} could not be run: {why.strerror}; install it, then run this again"
        ) from None
    if done.returncode:
        said = done.stderr.strip()
        raise stop.Stop(f"rn: {' '.join(command)} failed{': ' + said if said else ''}; {failed}")
    return done.stdout


def git(args: list[str], failed: str, fed: str | None = None) -> str:
    """What git prints for the arguments, with the text fed to its input; stops with what git said
    and the action given."""
    return ran(["git"] + args, failed, fed)


def at_top() -> None:
    """Returns when rn runs at the top of a git repository; stops otherwise."""
    below = git(["rev-parse", "--show-prefix"], "run rn inside the user's repository").strip()
    if below:
        raise stop.Stop(
            f"rn: this runs in {below} below the top of the repository; run it from the top,"
            ' after `cd "$(git rev-parse --show-toplevel)"`'
        )


def default_branch() -> str:
    """The remote's default branch, as git knows it, such as origin/main."""
    ref = git(
        ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        "run `git remote set-head origin --auto` so git knows the default branch, then run this"
        " again",
    )
    return ref.strip()


def base() -> str:
    """The commit the checked-out branch left the default branch at."""
    branch = default_branch()
    return git(
        ["merge-base", branch, "HEAD"],
        f"the checked-out branch shares no history with {branch}; fetch it whole with"
        " `git fetch --unshallow origin` where the clone is shallow, or check out the session's"
        " branch",
    ).strip()


def changed() -> list[str]:
    """Each path of the working tree changed since the last commit, every file of a folder not
    yet added among them."""
    listed = git(["status", "--porcelain", "-uall"], AS_GIT_SAYS)
    return [line[3:] for line in listed.splitlines()]


def at(commit: str, path: str) -> str | None:
    """The text of the file at the path as the commit holds it; None where it holds none."""
    if not git(["ls-tree", "--name-only", commit, "--", path], AS_GIT_SAYS):
        return None
    return git(["show", f"{commit}:{path}"], AS_GIT_SAYS)


def staged(path: str) -> str | None:
    """The text of the file at the path as git's index holds it, which each keep writes it to;
    None where it holds none."""
    if not git(["ls-files", "--", path], AS_GIT_SAYS):
        return None
    return git(["show", f":{path}"], AS_GIT_SAYS)


def held_path() -> str:
    """The path of the file holding the messages of the moves written since the last commit."""
    return git(["rev-parse", "--git-path", HELD], AS_GIT_SAYS).strip()


def held() -> list[str]:
    """The message of each move written since the last commit, in the order written; none where
    none is."""
    path = held_path()
    return read_text(path).split("\0")[:-1] if os.path.isfile(path) else []


def hold(message: str) -> None:
    """Holds the message of a move written for the commit its step ends with, once, as a move
    written again, such as by a fresh conversation, is the same move."""
    if message not in held():
        with open(held_path(), "a", encoding="utf-8") as f:
            f.write(message + "\0")


def let_go() -> None:
    """Lets go of the messages held, once a commit holds them."""
    path = held_path()
    if os.path.isfile(path):
        os.remove(path)


def read_text(path: str) -> str:
    """The text at the path."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path: str, text: str) -> None:
    """Writes the text at the path, making its folder where it is not there."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def add_line(path: str, data: Any) -> None:
    """Adds the data as JSON on one line at the end of the file at the path, making it where it is
    not there."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def write_json(path: str, data: Any) -> None:
    """Writes the data as JSON at the path, one key or value to a line, so the user can read it on
    the pull request."""
    write_text(path, json.dumps(data, ensure_ascii=False, indent=1) + "\n")


def dumped(data: Any) -> str:
    """The data as JSON on one line, with text beyond ASCII as it is, for the orchestrator to
    read."""
    return json.dumps(data, ensure_ascii=False)


def push() -> None:
    """Pushes the checked-out branch to the remote's branch of its name, tracking it; stops with
    what git said, that what is committed is not pushed, and that running the move again pushes it
    once it is fixed."""
    git(
        ["push", "-q", "-u", "origin", "HEAD"],
        "what is committed is not pushed: fix it as git says, then run this again, which pushes it",
    )


def pushed() -> None:
    """Returns when every change is committed and pushed, so a proposal shows what the user reads
    on the pull request; stops otherwise, saying how to keep or push it."""
    paths = changed()
    if paths:
        raise stop.Stop(
            f"rn: the record has changes not kept, {', '.join(paths)}; a proposal shows what is"
            " pushed alone, as the user reads it on the pull request, so keep the move with"
            " `rn.py state --next <n> --message <what it brought>` first, then run this again"
        )
    ahead = git(
        ["rev-list", "--count", "@{upstream}..HEAD"],
        "push the branch with `git push -u origin HEAD`, then run this again",
    ).strip()
    if int(ahead):
        raise stop.Stop(
            f"rn: the branch has {ahead} commit(s) not pushed; push with `git push`, then run this"
            " again"
        )


def gh(args: list[str], again: str) -> str:
    """What GitHub's command prints for the arguments; stops with what it said, to fix it as it
    says, and what to run again once it is fixed."""
    return ran(
        ["gh"] + args, f"fix it as gh says, such as with `gh auth login`, then {again}"
    ).strip()


def top() -> str:
    """The top of the repository rn runs in, as a whole path."""
    return git(["rev-parse", "--show-toplevel"], AS_GIT_SAYS).strip()


def branch() -> str:
    """The branch checked out."""
    return git(["branch", "--show-current"], AS_GIT_SAYS).strip()
