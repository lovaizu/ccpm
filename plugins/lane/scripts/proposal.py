"""Decides whether a Proposal can stand against the lane types, the plugin's Steps, and its files,
and keeps each Proposal shown by its ID with the Steps it came from and the conversation that
showed it, in `<temp>/lane/<yyyymmdd>-<plugin>/`, for the Run of up that showed it, if any: until
the caller approves it, the Steps change, or that Run ends without its approval."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from domain.laid_set import Lane, Move, Route
from domain.run_record import Run
from steps import Role


@dataclass(frozen=True)
class Proposal:
    """The lanes and the routes proposed from the Steps as they read at one time, the data model's
    Proposal, in the form of `domain/proposal.schema.json`: the plugin, each skill whose call begins
    a run of its own, each Lane with its sentence, each Route of each skill, the adapters named, the
    ID, the fingerprint of the Steps, and the ID of the conversation in which `lay.py print` showed
    it, "" for none."""

    plugin: str
    skills: tuple[str, ...]
    lanes: tuple[Lane, ...]
    routes: tuple[Route, ...]
    text_adapter: str = ""
    results_adapter: str = ""
    id: str = ""
    steps: str = ""
    conversation: str = ""


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
    there is, taking what its type takes; each skill a skill of the plugin, with a Route `first`,
    and each Route of a skill of the Proposal; each Role reached by the Routes and each Result named
    by a Route; each subagent's file setting `background: true`; each command that a Route waits for
    or goes after setting `disable-model-invocation: true`; each program in `hooks/adapters/` named;
    and no two Roles taking their Steps from one file."""
    raise NotImplementedError("proposal.check")


def moves_of(proposal: Proposal, skill: str, after: str) -> tuple[Move, ...]:
    """The moves of the skill's Route after the moment, none where no Route of it goes after it."""
    raise NotImplementedError("proposal.moves_of")


def keep(proposal: Proposal, found: Sequence[Role], temp: str, conversation: str = "") -> Proposal:
    """Keeps the Proposal, with the sentence of each Lane made by its type, the fingerprint of the
    Roles' Steps it came from, and the ID of the conversation that showed it, "" for none, under a
    new ID of 8 hex digits, and gives it with its ID."""
    raise NotImplementedError("proposal.keep")


def kept(temp: str, plugin: str, id: str) -> Proposal | None:
    """The Proposal kept for the plugin under the ID, or None where none is."""
    raise NotImplementedError("proposal.kept")


def waits(proposal: Proposal, run: Run | None) -> bool:
    """Whether the Proposal can still be laid as far as the Run of up that showed it goes, given
    the Run of up of the conversation that showed it, None where that conversation has none: true
    where it has none, as no Run of up showed the Proposal, or where its Run goes on and showed this
    Proposal last; false where that Run ended, or showed another Proposal since, as a later Run of
    up in the same conversation does."""
    raise NotImplementedError("proposal.waits")
