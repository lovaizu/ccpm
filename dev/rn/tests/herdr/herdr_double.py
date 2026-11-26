"""The double of herdr that rn's unit cases run in its place. It answers each command of herdr
that rn's code runs from one line of herdr 0.9.5's record in recorded/: `herdr worktree open`,
which opens a worktree in a workspace; `herdr worktree list`, which lists the repository's
worktrees, or can't; and `herdr worktree remove`, which removes a workspace's worktree, or finds no
such workspace, as the plugin guide's Each result of a double from a record says. A command that
no record holds fails with exit 1, naming itself.

It keeps its state, each worktree open in a workspace, by its path, in a JSON file of the folder
it's given, and it removes a worktree by git, as herdr does, so that the case sees it gone."""

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
# The file of the double's state in the folder it's given.
STATE = "herdr-state.json"


@functools.cache
def _record() -> list[dict[str, Any]]:
    with open(os.path.join(RECORDED, WORKTREE), encoding="utf-8") as f:
        return [json.loads(each) for each in f]


def _line(event: str) -> dict[str, Any]:
    return copy.deepcopy(next(each for each in _record() if each["event"] == event))


def state(folder: str) -> dict[str, Any]:
    """The double's state in the folder: `open`, each worktree open in a workspace, its path to its
    workspace's id, `lists`, whether herdr lists the worktrees, and `asked`, each herdr command it
    was asked, by its words."""
    path = os.path.join(folder, STATE)
    if not os.path.exists(path):
        return {"open": {}, "lists": True, "asked": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def unlisted(folder: str) -> None:
    """Sets the double's state to herdr not listing the worktrees, as where it can't."""
    kept = state(folder)
    kept["lists"] = False
    _keep(folder, kept)


def _keep(folder: str, kept: dict[str, Any]) -> None:
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, STATE), "w", encoding="utf-8") as f:
        json.dump(kept, f)


def answer(argv: Sequence[str], folder: str) -> tuple[int, str, str]:
    """What herdr gives for the command's words, from `herdr` on, as the record shows, with the
    state in the folder kept."""
    kept = state(folder)
    kept["asked"].append(list(argv))
    words = list(argv)
    given = _ANSWERS.get(" ".join(words[1:3]), _unrecorded)(kept, words)
    _keep(folder, kept)
    return int(given["exit"]), str(given.get("stdout", "")), str(given.get("stderr", ""))


def _option(words: list[str], name: str) -> str:
    return words[words.index(name) + 1] if name in words else ""


def _filled(text: str, path: str, workspace: str) -> str:
    branch = os.path.basename(path)
    return (
        text.replace("{path}", path)
        .replace("{repository}", os.path.dirname(os.path.dirname(os.path.dirname(path))))
        .replace("{workspace}", workspace)
        .replace("{branch}", branch)
        .replace("{label}", branch)
        .replace("{terminal}", f"term_{workspace}")
    )


def _unrecorded(kept: dict[str, Any], words: list[str]) -> dict[str, Any]:
    return {"exit": 1, "stderr": f"herdr double: no record of {' '.join(words)}\n"}


def _opened(kept: dict[str, Any], words: list[str]) -> dict[str, Any]:
    path = _option(words, "--path")
    workspace = kept["open"].setdefault(path, f"w{len(kept['open']) + 2}")
    given = _line("herdr worktree open opens the worktree in a workspace")
    given["stdout"] = _filled(given["stdout"], path, workspace)
    return given


def _listed(kept: dict[str, Any], words: list[str]) -> dict[str, Any]:
    if not kept["lists"]:
        return _line("herdr worktree list can't list the worktrees")
    given = _line("herdr worktree list lists the repository's worktrees")
    template = json.dumps(given.pop("worktree"))
    listed = [json.loads(_filled(template, path, each)) for path, each in kept["open"].items()]
    shown = json.loads(given["stdout"].replace("{repository}", _option(words, "--cwd")))
    shown["result"]["worktrees"] = listed
    given["stdout"] = json.dumps(shown, separators=(",", ":")) + "\n"
    return given


def _removed(kept: dict[str, Any], words: list[str]) -> dict[str, Any]:
    workspace = _option(words, "--workspace")
    paths = [path for path, each in kept["open"].items() if each == workspace]
    if not paths:
        given = _line("herdr worktree remove finds no such workspace")
        given["stderr"] = given["stderr"].replace("{workspace}", workspace)
        return given
    path = paths[0]
    subprocess.run(
        ["git", "worktree", "remove", "--force", path],
        cwd=os.path.dirname(path),
        capture_output=True,
        check=True,
    )
    del kept["open"][path]
    given = _line("herdr worktree remove removes the worktree of the workspace")
    given["stdout"] = _filled(given["stdout"], path, workspace)
    return given


# What the double gives for each command of herdr, by its two words after `herdr`.
_ANSWERS = {"worktree open": _opened, "worktree list": _listed, "worktree remove": _removed}
