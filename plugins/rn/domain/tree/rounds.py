"""Decides where each Round lies in the run's folder: `rounds/<n>/` for the n-th Round of the run,
holding the Cut of each start, `<role>[-<group>].cut.json`, and its result beside it,
`<role>[-<group>].json`."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from dataclasses import dataclass

from fault import Wrong
from schemas.form import Json

_CUT = ".cut.json"
_TREE = "design-tree.json"
_WORKTREES = os.path.join(".claude", "worktrees")


@dataclass(frozen=True)
class Start:
    """One start of a Round: its number, its role, the group an evaluator judges, or "" for the
    generator, its Cut, and its result, or None while it has none."""

    round: int
    role: str
    group: str
    cut: Json
    result: Json | None


def each(run: str) -> Sequence[Start]:
    """Each start of the run's Rounds, in the order they were cut: by the Round's number, the
    generator before the evaluators, and the evaluators by their group.

    Takes: the run's folder.
    Gives: each start, its result None where its role was stopped or still runs.
    Refuses: Wrong, naming the file, where a Cut or a result isn't JSON."""
    folder = os.path.join(run, "rounds")
    if not os.path.isdir(folder):
        return []
    starts: list[Start] = []
    for number in sorted((n for n in os.listdir(folder) if n.isdigit()), key=int):
        names = [n for n in os.listdir(os.path.join(folder, number)) if n.endswith(_CUT)]
        for name in sorted(names, key=lambda n: (n != f"generator{_CUT}", n)):
            role, _, group = name.removesuffix(_CUT).partition("-")
            cut = os.path.join("rounds", number, name)
            result = cut.removesuffix(_CUT) + ".json"
            given = _read(run, result) if os.path.isfile(os.path.join(run, result)) else None
            starts.append(Start(int(number), role, group, _read(run, cut), given))
    return starts


def folder(top: str) -> str | None:
    """The run's folder that a conversation goes on with.

    Takes: the folder that the conversation works in: the repository's root, or rn's worktree of a
    run once the conversation entered it.
    Gives: from `top`, the folder of `.rn/` in `top` or in rn's worktree of a run,
    `.claude/worktrees/rn-*/`, whose design tree has work left, the one changed last where several
    have; None where none has, as a run merged has no work left.
    Refuses: nothing."""
    found = [
        (os.path.getmtime(os.path.join(top, run, _TREE)), run)
        for base in ("", *_worktrees(top))
        for run in _runs(top, base)
        if _left(os.path.join(top, run, _TREE))
    ]
    return max(found)[1] if found else None


def _worktrees(top: str) -> list[str]:
    """Each of rn's worktrees of a run in `top`, from `top`."""
    held = os.path.join(top, _WORKTREES)
    names = sorted(os.listdir(held)) if os.path.isdir(held) else []
    return [os.path.join(_WORKTREES, n) for n in names if n.startswith("rn-")]


def _runs(top: str, base: str) -> list[str]:
    """Each folder of `.rn/` under `base`, from `top`, that holds a design tree."""
    rn = os.path.join(top, base, ".rn")
    names = sorted(os.listdir(rn)) if os.path.isdir(rn) else []
    held = [os.path.join(base, ".rn", n) for n in names]
    return [r for r in held if os.path.isfile(os.path.join(top, r, _TREE))]


def _left(tree: str) -> bool:
    """Whether the design tree at `tree` has work left; a file that isn't JSON has none."""
    with open(tree, encoding="utf-8") as f:
        try:
            return bool(json.load(f).get("work"))
        except ValueError:
            return False


def path(run: str, start: Start) -> str:
    """Where the start's Cut lies.

    Takes: the run's folder and a start.
    Gives: the path of its Cut, which its result lies beside.
    Refuses: nothing."""
    name = f"{start.role}-{start.group}" if start.group else start.role
    return f"{run}/rounds/{start.round}/{name}{_CUT}"


def _read(run: str, name: str) -> Json:
    """The JSON of the file `name` in the run's folder; Wrong, naming it, where it isn't JSON."""
    with open(os.path.join(run, name), encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError as error:
            raise Wrong(f"{name}: isn't JSON: {error}") from None
