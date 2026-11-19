"""Decides where each Round lies in the run's folder: `rounds/<n>/` for the n-th Round of the run,
holding the Cut of each start, `<role>[-<group>].cut.json`, and its result beside it,
`<role>[-<group>].json`."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from schemas.form import Json


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
    """Each start of the run's Rounds, in the order they were cut.

    Takes: the run's folder.
    Gives: each start, its result None where its role was stopped or still runs.
    Refuses: Wrong, naming the file, where a Cut or a result isn't JSON."""
    raise NotImplementedError("rounds.each")


def path(run: str, start: Start) -> str:
    """Where the start's Cut lies.

    Takes: the run's folder and a start.
    Gives: the path of its Cut, which its result lies beside.
    Refuses: nothing."""
    raise NotImplementedError("rounds.path")
