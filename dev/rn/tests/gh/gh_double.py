"""The double of gh that rn's cases run in its place, as rn's Test strategy says under Integration
testing and Contract testing. It answers each command of gh that rn's code runs from one line of a
record in recorded/: gh 2.102.1's runs for `gh auth status` and `gh pr view`, and gh's manual for
`gh pr create`, as the plugin guide's Each result of a double from a record says. A command that no
record holds fails with exit 1, naming itself, so that a body that runs it shows the gap.

It serves two ways in: `host`, a Host of repository.host for the unit cases, which runs git for
real and gh from the records; and `program`, a `gh` written into a folder for the integration
cases, put first on the PATH of each command that the double of Claude Code runs. Each keeps its
state, whether the person is logged in and the pull request it opened, in a JSON file of the folder
it's given, and each command it was asked in the same file."""

from __future__ import annotations

import copy
import functools
import json
import os
import subprocess
from collections.abc import Sequence
from typing import Any

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")
AUTH = "gh-2.102.1-auth.jsonl"
PR_VIEW = "gh-2.102.1-pr-view.jsonl"
MANUAL = "gh-manual.jsonl"
# The file of the double's state in the folder it's given.
STATE = "gh-state.json"


@functools.cache
def _record(record: str) -> list[dict[str, Any]]:
    with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
        return [json.loads(each) for each in f]


def line(record: str, event: str) -> dict[str, Any]:
    """A copy of the line of the record in recorded/ that the event names."""
    return copy.deepcopy(next(each for each in _record(record) if each["event"] == event))


def state(folder: str) -> dict[str, Any]:
    """The double's state in the folder: `logged_in`, `pull_request` (the URL it opened, or None),
    and `asked`, each gh command it was asked, by its words."""
    path = os.path.join(folder, STATE)
    if not os.path.exists(path):
        return {"logged_in": True, "pull_request": None, "asked": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def keep(folder: str, kept: dict[str, Any]) -> None:
    """Writes the double's state in the folder."""
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, STATE), "w", encoding="utf-8") as f:
        json.dump(kept, f)


def logged_out(folder: str) -> None:
    """Sets the double's state to no login, as `gh auth status` finds none."""
    kept = state(folder)
    kept["logged_in"] = False
    keep(folder, kept)


def answer(argv: Sequence[str], folder: str) -> tuple[int, str, str]:
    """What gh gives for the command's words, from `gh` on, as the records show, with the state
    in the folder kept."""
    kept = state(folder)
    kept["asked"].append(list(argv))
    words = list(argv[1:3])
    if not kept["logged_in"]:
        given = line(AUTH, "gh auth status finds no login")
    elif words == ["auth", "status"]:
        given = line(AUTH, "gh auth status finds the login")
    elif words == ["pr", "view"] and kept["pull_request"] is None:
        given = line(PR_VIEW, "gh pr view finds no pull request for the branch")
        given["stderr"] = given["stderr"].replace("no-such-branch-rn", _branch(argv))
    elif words == ["pr", "view"]:
        given = line(PR_VIEW, "gh pr view gives the pull request with its comments")
        shown = json.loads(given["stdout"])
        shown.update(url=kept["pull_request"], comments=[])
        given["stdout"] = json.dumps(shown) + "\n"
    elif words == ["pr", "create"] and kept["pull_request"] is None:
        given = line(MANUAL, "gh pr create prints the URL of the pull request")
        kept["pull_request"] = given["stdout"].strip()
    else:
        given: dict[str, Any] = {"exit": 1, "stderr": f"gh double: no record of {' '.join(argv)}\n"}
    keep(folder, kept)
    return int(given["exit"]), str(given.get("stdout", "")), str(given.get("stderr", ""))


def _branch(argv: Sequence[str]) -> str:
    """The branch or number that `gh pr view` names, else the empty string."""
    named = [each for each in argv[3:] if not each.startswith("-")]
    return named[0] if named else ""


def host(folder: str) -> Any:
    """A Host that runs git for real, in the folder it's given, and answers gh from the records,
    with its state in `folder`; each command it ran is kept in `<folder>/gh-state.json`'s `asked`
    for gh, and in the Host's `ran` for both."""
    from repository.host import Ran as HostRan

    ran: list[tuple[list[str], str]] = []

    def run(argv: Sequence[str], cwd: str, env: Any = None) -> HostRan:
        ran.append((list(argv), cwd))
        if argv[0] == "gh":
            return HostRan(*answer(argv, folder))
        whole = {**os.environ, **env} if env else None
        done = subprocess.run(
            list(argv), cwd=cwd, env=whole, capture_output=True, text=True, check=False
        )
        return HostRan(done.returncode, done.stdout, done.stderr)

    run.ran = ran  # type: ignore[attr-defined]
    return run


def program(bin_folder: str, state_folder: str) -> str:
    """Writes `gh` into the bin folder, a program that answers as `answer` does with its state in
    the state folder, and gives the bin folder."""
    os.makedirs(bin_folder, exist_ok=True)
    path = os.path.join(bin_folder, "gh")
    here = os.path.dirname(os.path.abspath(__file__))
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            f"sys.path.insert(0, {here!r})\n"
            "import gh_double\n"
            f"code, out, err = gh_double.answer(['gh', *sys.argv[1:]], {state_folder!r})\n"
            "sys.stdout.write(out)\n"
            "sys.stderr.write(err)\n"
            "sys.exit(code)\n"
        )
    os.chmod(path, 0o755)
    return bin_folder
