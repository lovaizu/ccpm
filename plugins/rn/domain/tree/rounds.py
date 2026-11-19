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
    """The run's folder of a worktree.

    Takes: the top of the worktree.
    Gives: the latest folder of `.rn/` that holds a design tree, from the top, as each run works in
    a worktree of its own; None where none is there.
    Refuses: nothing."""
    rn = os.path.join(top, ".rn")
    found = sorted(
        name
        for name in (os.listdir(rn) if os.path.isdir(rn) else [])
        if os.path.isfile(os.path.join(rn, name, "design-tree.json"))
    )
    return f".rn/{found[-1]}" if found else None


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
