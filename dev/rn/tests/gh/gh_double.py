"""The double of gh that rn's cases run in its place, as rn's Test strategy says under Integration
testing and Contract testing. It answers each command of gh that rn's code runs from one line of a
record in recorded/: gh 2.102.1's runs for `gh auth status`, `gh pr view`, with the state of a
pull request that is open, closed, or merged, and where gh can't reach GitHub, `gh pr close`, and
`gh pr checks --watch`, and gh's manual for `gh pr create`, as the plugin guide's Each result of a
double from a record says. A command that no record holds fails with exit 1, naming itself, so
that a body that runs it shows the gap.

It serves two ways in: `host`, a Host of repository.host for the unit cases, which runs git for
real and gh from the records; and `program`, a `gh` written into a folder for the integration
cases, put first on the PATH of each command that the double of Claude Code runs. Each keeps its
state, whether the person is logged in and GitHub is reached, the pull request it opened, an
earlier one of the branch that isn't open, and what its CI's checks found, in a JSON file of the
folder it's given, and each command it was asked in the same file."""

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
PR_CHECKS = "gh-2.102.1-pr-checks.jsonl"
PR_CLOSE = "gh-2.102.1-pr-close.jsonl"
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
    """The double's state in the folder: `logged_in`, `reached`, whether gh reaches GitHub,
    `closes`, whether it reaches GitHub to close a pull request once it read it,
    `pull_request` (the URL of the open one, or None), `earlier`, an earlier pull request of the
    branch that isn't open, as its `url` and `state`, `CLOSED` or `MERGED`, or None, `checks`,
    what the CI's checks found, `passed`, `failed`, or `none`, and `asked`, each gh command it was
    asked, by its words."""
    path = os.path.join(folder, STATE)
    if not os.path.exists(path):
        return {
            "logged_in": True,
            "reached": True,
            "closes": True,
            "pull_request": None,
            "earlier": None,
            "checks": "passed",
            "asked": [],
        }
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


def unreached(folder: str) -> None:
    """Sets the double's state to GitHub out of reach, as gh finds where the network is down."""
    kept = state(folder)
    kept["reached"] = False
    keep(folder, kept)


def closes_unreached(folder: str) -> None:
    """Sets the double's state to GitHub out of reach once gh has read the pull request, so that
    `gh pr close` fails as where the network goes down."""
    kept = state(folder)
    kept["closes"] = False
    keep(folder, kept)


def opened(folder: str, url: str) -> None:
    """Sets the pull request of the URL as open, as `gh pr create` leaves it."""
    kept = state(folder)
    kept["pull_request"] = url
    keep(folder, kept)


def earlier(folder: str, url: str, held: str) -> None:
    """Sets an earlier pull request of the branch, of the URL, as `CLOSED` or `MERGED`, as an
    earlier run of the same branch's name leaves it."""
    kept = state(folder)
    kept["earlier"] = {"url": url, "state": held}
    keep(folder, kept)


def checks(folder: str, found: str) -> None:
    """Sets what the CI's checks found: `passed`, `failed`, or `none`, where it has no checks."""
    kept = state(folder)
    kept["checks"] = found
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
    else:
        given = _ANSWERS.get(" ".join(words), _unrecorded)(kept, argv)
    keep(folder, kept)
    return int(given["exit"]), str(given.get("stdout", "")), str(given.get("stderr", ""))


def _unrecorded(kept: dict[str, Any], argv: Sequence[str]) -> dict[str, Any]:
    """What the double gives for a command that no record holds: exit 1, naming it."""
    return {"exit": 1, "stderr": f"gh double: no record of {' '.join(argv)}\n"}


def _viewed(kept: dict[str, Any], argv: Sequence[str]) -> dict[str, Any]:
    """What `gh pr view` gives, by the fields that `--json` names."""
    if not kept["reached"]:
        return line(PR_VIEW, "gh pr view can't reach GitHub")
    if "state" in _fields(argv):
        return _state(kept, argv)
    if kept["pull_request"] is None and kept["earlier"] is None:
        given = line(PR_VIEW, "gh pr view finds no pull request for the branch")
        given["stderr"] = given["stderr"].replace("no-such-branch-rn", _branch(argv))
        return given
    given = line(PR_VIEW, "gh pr view gives the pull request with its comments")
    shown = json.loads(given["stdout"])
    shown.update(url=kept["pull_request"] or kept["earlier"]["url"], comments=[])
    given["stdout"] = json.dumps(shown) + "\n"
    return given


def _closed(kept: dict[str, Any], argv: Sequence[str]) -> dict[str, Any]:
    """What `gh pr close <URL>` gives, closing the open pull request of the URL."""
    if not (kept["reached"] and kept["closes"]):
        return line(PR_CLOSE, "gh pr close can't reach GitHub")
    if kept["pull_request"] not in argv[3:]:
        return _unrecorded(kept, argv)
    kept["earlier"] = {"url": kept["pull_request"], "state": "CLOSED"}
    kept["pull_request"] = None
    return line(PR_CLOSE, "gh pr close closes the open pull request")


def _created(kept: dict[str, Any], argv: Sequence[str]) -> dict[str, Any]:
    """What `gh pr create` gives, opening the pull request where none is open."""
    if kept["pull_request"] is not None:
        return _unrecorded(kept, argv)
    given = line(MANUAL, "gh pr create prints the URL of the pull request")
    kept["pull_request"] = given["stdout"].strip()
    return given


def _checks(kept: dict[str, Any], argv: Sequence[str]) -> dict[str, Any]:
    """What `gh pr checks --watch` gives of the open pull request's CI."""
    if kept["pull_request"] is None:
        return _unrecorded(kept, argv)
    return _checked(kept["checks"])


def _state(kept: dict[str, Any], argv: Sequence[str]) -> dict[str, Any]:
    """What `gh pr view <branch> --json state,url` gives: the open pull request where there is one,
    else the earlier one, as gh 2.102.1 takes an open one before any other, else the newest."""
    if kept["pull_request"] is not None:
        given = line(PR_VIEW, "gh pr view gives the open pull request of the branch")
        url = kept["pull_request"]
    elif kept["earlier"] is not None and kept["earlier"]["state"] == "MERGED":
        given = line(PR_VIEW, "gh pr view gives the merged pull request of the branch")
        url = kept["earlier"]["url"]
    elif kept["earlier"] is not None:
        given = line(PR_VIEW, "gh pr view gives the closed pull request of the branch")
        url = kept["earlier"]["url"]
    else:
        given = line(PR_VIEW, "gh pr view finds no pull request for the branch")
        given["stderr"] = given["stderr"].replace("no-such-branch-rn", _branch(argv))
        return given
    shown = json.loads(given["stdout"])
    shown["url"] = url
    given["stdout"] = json.dumps(shown, separators=(",", ":")) + "\n"
    return given


def _fields(argv: Sequence[str]) -> list[str]:
    """The fields that `--json` names, else none."""
    words = list(argv)
    if "--json" not in words or words.index("--json") + 1 == len(words):
        return []
    return words[words.index("--json") + 1].split(",")


def _checked(found: str) -> dict[str, Any]:
    """What `gh pr checks --watch` gives where the CI's checks found `passed`, `failed`, or
    `none`."""
    if found == "failed":
        return line(PR_CHECKS, "gh pr checks --watch finds a check failed")
    if found == "none":
        return line(PR_CHECKS, "gh pr checks --watch finds no checks")
    return line(PR_CHECKS, "gh pr checks --watch finds each check passed")


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


# What the double gives for each command of gh but `gh auth status`, by its two words after `gh`.
_ANSWERS = {"pr view": _viewed, "pr close": _closed, "pr create": _created, "pr checks": _checks}
