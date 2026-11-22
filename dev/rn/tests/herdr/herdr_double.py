"""The double of herdr that rn's unit cases run in its place. It answers each command of herdr that
rn's code runs from one line of recorded/herdr-0.9.5-worktree.jsonl, herdr 0.9.5's runs in a
throwaway repository, as the plugin guide's Each result of a double from a record says. Where
herdr's run changed the repository, the double makes the same change with git: `herdr worktree
create` adds the worktree on a new branch from the base, as `git worktree add -b` does, and `herdr
worktree open` changes no file. A command that no record holds fails with exit 1, naming itself, so
that a body that runs it shows the gap.

It serves as `host`, a Host of repository.host that wraps another, such as the double of gh's, and
passes each command but herdr's to it, so that no case reaches the herdr that the developer runs
in."""

from __future__ import annotations

import copy
import functools
import json
import os
import subprocess
from collections.abc import Sequence
from typing import Any

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")
WORKTREE = "herdr-0.9.5-worktree.jsonl"
CREATED = (
    "herdr worktree create makes the worktree on a new branch from the base and opens its workspace"
)
OPENED = "herdr worktree open opens the workspace of the worktree that git made"
NOT_FOUND = "herdr worktree open fails where no worktree lies at the path"
NOT_RUNNING = "herdr worktree open fails where no herdr server is running"


@functools.cache
def _record(record: str) -> list[dict[str, Any]]:
    with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
        return [json.loads(each) for each in f]


def line(record: str, event: str) -> dict[str, Any]:
    """A copy of the line of the record in recorded/ that the event names."""
    return copy.deepcopy(next(each for each in _record(record) if each["event"] == event))


def host(inner: Any, running: bool = True) -> Any:
    """A Host that answers herdr from the records and passes each other command to `inner`.

    `running` False gives herdr with no server running, which fails each command as the record
    shows. Each herdr command it was asked is kept in the Host's `asked`, with the folder it ran
    in."""
    from repository.host import Ran

    asked: list[tuple[list[str], str]] = []

    def run(argv: Sequence[str], cwd: str, env: Any = None) -> Ran:
        if argv[0] != "herdr":
            return inner(argv, cwd, env)
        asked.append((list(argv), cwd))
        given = _answer(list(argv), cwd, running)
        return Ran(int(given["exit"]), str(given["stdout"]), str(given["stderr"]))

    run.asked = asked  # type: ignore[attr-defined]
    return run


def _answer(argv: list[str], cwd: str, running: bool) -> dict[str, Any]:
    """What herdr gives for the command's words, as the records show, with herdr's change made."""
    words, options = argv[1:3], _options(argv[3:])
    if not running:
        given = line(WORKTREE, NOT_RUNNING)
        given["stderr"] = given["stderr"].replace("worktree:open", f"worktree:{argv[2]}")
        return given
    if words == ["worktree", "create"] and {"branch", "base", "path"} <= options.keys():
        add = ["git", "worktree", "add", "-q", "-b", options["branch"], options["path"]]
        made = subprocess.run(
            [*add, options["base"]], cwd=options.get("cwd", cwd), capture_output=True, check=False
        )
        if made.returncode == 0:
            return line(WORKTREE, CREATED)
    if words == ["worktree", "open"] and "path" in options and "branch" not in options:
        if os.path.isfile(os.path.join(options["path"], ".git")):
            return line(WORKTREE, OPENED)
        return line(WORKTREE, NOT_FOUND)
    return {"exit": 1, "stdout": "", "stderr": f"herdr double: no record of {' '.join(argv)}\n"}


def _options(given: list[str]) -> dict[str, str]:
    """Each option of the words that takes a value, by its name without `--`."""
    return {
        name[2:]: value
        for name, value in zip(given, given[1:] + [""])
        if name.startswith("--") and not value.startswith("--")
    }
