"""The work's branch of the user's repository, by git, and its one draft pull request, by GitHub's
command `gh`: each commit of a run on the branch `rn/<the run's name>`, which the run's first
commit makes from where the repository stands; the branch pushed to `origin`; a draft pull
request opened for it once, and found again after; and the messages of the run's commits, which
hold each decision taken without asking the user."""

from __future__ import annotations

import os
import subprocess

# The trailer each commit of a run ends with, naming the run, by which rn finds its commits.
TRAILER = "Rn-Run: "
REMOTE = "origin"


class Failed(Exception):
    """A git or gh command that came back with an error. The message says the command and what it
    printed."""


def ran(*command: str) -> str:
    """What the command printed, its blanks at the ends left out; refuses, by Failed, a command
    that's not there or comes back with an error."""
    try:
        done = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        raise Failed(f"`{command[0]}` isn't installed") from None
    if done.returncode:
        said = (done.stderr.strip() or done.stdout.strip()).splitlines()
        # git and gh say what went wrong on a line of its own, before any usage or hint.
        first = [s for s in said if s.startswith(("fatal:", "error:"))] or said[-1:]
        raise Failed(f"`{' '.join(command[:3])}` gave: {first[0] if first else done.returncode}")
    return done.stdout.strip()


def branch(run: str) -> str:
    """The name of the run's branch."""
    return f"rn/{os.path.basename(os.path.normpath(run))}"


def on_branch(run: str) -> None:
    """Checks out the run's branch, made from where the repository stands where it's not there."""
    name = branch(run)
    if ran("git", "branch", "--show-current") == name:
        return
    exists = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{name}"],
        capture_output=True,
        check=False,
    )
    ran("git", "switch", *([] if exists.returncode == 0 else ["-c"]), name)


def branch_runs() -> list[str]:
    """Each run that a branch of rn's, `rn/<name>`, holds the design tree of, by its folder."""
    try:
        said = ran("git", "for-each-ref", "--format=%(refname:short)", "refs/heads/rn/")
    except Failed:
        return []
    found = []
    for name in said.splitlines():
        run = os.path.join(".rn", name[len("rn/") :])
        if committed(run, os.path.join(run, "design-tree.json")) is not None:
            found.append(run)
    return found


def committed(run: str, path: str) -> str | None:
    """The file at the path as the run's branch last committed it; None where the branch or the
    file isn't there."""
    done = subprocess.run(
        ["git", "show", f"{branch(run)}:{path}"], capture_output=True, text=True, check=False
    )
    return done.stdout if done.returncode == 0 else None


def commit(run: str, paths: list[str], message: str) -> bool:
    """Commits the paths on the run's branch with the message, the trailer naming the run after
    it: whether there was a change of them to commit."""
    on_branch(run)
    ran("git", "add", "-A", "--", *paths)
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", *paths], capture_output=True, check=False
    )
    if staged.returncode == 0:
        return False
    ran("git", "commit", "-q", "-m", f"{message}\n\n{TRAILER}{run}", "--", *paths)
    return True


def push(run: str, title: str, body: str) -> str:
    """Pushes the run's branch, and opens its draft pull request where it has none: the pull
    request's address. Refuses, by Failed, a push or a pull request that git or gh can't make,
    the commits kept on the branch."""
    name = branch(run)
    ran("git", "push", "-q", "-u", REMOTE, name)
    try:
        return ran("gh", "pr", "view", name, "--json", "url", "--jq", ".url")
    except Failed:
        pass
    made = ran("gh", "pr", "create", "--draft", "--head", name, "--title", title, "--body", body)
    return made.splitlines()[-1]


def messages(run: str) -> list[str]:
    """The message of each commit of the run on its branch, the first first."""
    try:
        said = ran("git", "log", "--reverse", "--format=%B%x00", branch(run), "--")
    except Failed:
        return []
    marked = f"{TRAILER}{run}"
    return [m.strip() for m in said.split("\0") if marked in m]
