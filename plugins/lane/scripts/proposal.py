"""Decides whether a Proposal can stand against the lane types, the plugin's Steps, and its files,
and keeps each Proposal shown by its ID with the Steps it came from, in
`<temp>/lane/<yyyymmdd>-<plugin>/`, until the caller approves it or the Steps change."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from domain.laid_set import Lane, Move, Route
from steps import Role


@dataclass(frozen=True)
class Proposal:
    """The lanes and the routes proposed from the Steps as they read at one time, the data model's
    Proposal, in the form of `domain/proposal.schema.json`: the plugin, its skill, each Lane with
    its sentence, each Route, the adapters named, the ID, and the fingerprint of the Steps."""

    plugin: str
    skill: str
    lanes: tuple[Lane, ...]
    routes: tuple[Route, ...]
    text_adapter: str = ""
    results_adapter: str = ""
    id: str = ""
    steps: str = ""


@dataclass(frozen=True)
class Refusal:
    """Why a Proposal can't stand: each fault, and whether up mends it, or the user mends a file of
    the plugin, such as a subagent's file without `background: true`."""

    faults: tuple[str, ...]
    in_files: bool


def parse(given: Any, where: str) -> Proposal:
    """The Proposal of the JSON value that up wrote to the file at `where`, without sentences, ID,
    or fingerprint. Raises Fault, naming the field and what the form takes, with up to mend it,
    where it isn't in the form of `domain/proposal.schema.json`."""
    raise NotImplementedError("proposal.parse")


def check(proposal: Proposal, found: Sequence[Role], plugin_root: str) -> Refusal | None:
    """Why the Proposal can't stand, or None where it can: each Lane of a type there is, on a Step
    there is, taking what its type takes; each Role reached by the Routes and each Result named by a
    Route; each subagent's file setting `background: true`; each command that a Route waits for or
    goes after setting `disable-model-invocation: true`; each program in `hooks/adapters/` named;
    and no two Roles taking their Steps from one file."""
    raise NotImplementedError("proposal.check")


def moves_of(proposal: Proposal, after: str) -> tuple[Move, ...]:
    """The moves of the Proposal's Route after the moment, none where no Route goes after it."""
    raise NotImplementedError("proposal.moves_of")


def keep(proposal: Proposal, found: Sequence[Role], temp: str) -> Proposal:
    """Keeps the Proposal, with the sentence of each Lane made by its type and the fingerprint of
    the Roles' Steps it came from, under a new ID of 8 hex digits, and gives it with its ID."""
    raise NotImplementedError("proposal.keep")


def kept(temp: str, plugin: str, id: str) -> Proposal | None:
    """The Proposal kept for the plugin under the ID, or None where none is."""
    raise NotImplementedError("proposal.kept")
