"""How each Run of a conversation stands, worked out from the run record's lines, the Routes, and
the Kept results alone: its Starts, its Results, its Approvals, the moves due, and whether it waits,
stands aside, or has ended."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from adapters import KeptResult
from form import Move, Route
from run_record import Line, Shown


class OffRoutes(Exception):
    """Kept results that the Routes don't lead through, with the first that leaves them, so that the
    guard stops the command with why and who must fix it."""


@dataclass(frozen=True)
class Result:
    """A Result that a role or the skill gave in the Run."""

    role: str
    result: str


@dataclass(frozen=True)
class Start:
    """One start or resume of a role in the Run: its role, text, and run values, the call that made
    it, the agent_id it's tied to once tied, each Result it gave, and whether it has ended."""

    role: str
    text: str
    values: Mapping[str, str]
    tool_use_id: str
    agent_id: str | None
    results: tuple[str, ...]
    ended: bool


@dataclass(frozen=True)
class Approval:
    """The caller's own act on a Proposal that the Run showed: a person's reply after it, or the
    Run's call by an AI."""

    proposal_id: str
    by: Literal["person", "ai"]


@dataclass(frozen=True)
class Due:
    """A move due, with the text and run values of a start or resume."""

    move: Move
    text: str
    values: Mapping[str, str]


@dataclass(frozen=True)
class Run:
    """One run of one skill in the conversation, as it stands."""

    id: str
    skill: str
    by: Literal["person", "ai"]
    words: str
    starts: tuple[Start, ...]
    results: tuple[Result, ...]
    shown: tuple[Shown, ...]
    approvals: tuple[Approval, ...]
    due: tuple[Move, ...]
    aside: bool
    ended: bool


@dataclass(frozen=True)
class Conversation:
    """Each Run of one conversation."""

    session_id: str
    runs: tuple[Run, ...]


def stand(session_id: str, lines: Sequence[Line], routes: Sequence[Route]) -> Conversation:
    """Where each Run of the conversation stands.

    Takes: the conversation's session_id, the run record's lines, and the plugin's Routes.
    Gives: each Run, its moves due those of the Route after its latest start, Result, typed command,
    or returned call, a Route after a typed command taking the place of those before; a Run ended
    by a Result whose move starts no more.
    Changes: nothing.
    Refuses: nothing; a line of a Run that the Routes no longer name leaves that Run no moves due.
    Carries: the guard's working out of each Run on each event of S1 to S7, from `G->>RS: reads
    the lines`.
    """
    raise NotImplementedError


def where(root: str, session_id: str) -> Conversation:
    """Where each Run of the conversation stands, for a script that isn't a hook.

    Takes: the plugin's folder, whose hooks/lanes.json gives the Routes, and the session_id from
    the script's CLAUDE_CODE_SESSION_ID.
    Gives: the Conversation, as `stand` works it out from the conversation's run record.
    Changes: nothing.
    Refuses: run_record.Unreadable, and form.OutOfForm or FileNotFoundError for lanes.json, so
    that the script refuses with why.
    Carries: S2 `L->>G: asks where up's Run stands`, S6 `R->>G: asks where each Run stands`.
    """
    raise NotImplementedError


def may_give(conversation: Conversation, role: str, routes: Sequence[Route]) -> tuple[str, ...]:
    """The Results that a role may give now in a Run of the conversation.

    Takes: the Conversation, the role or skill, and the Routes.
    Gives: each Result that a Route goes after for the role, or that a move due of the skill names
    to start no more by, in a Run that hasn't ended and, for a role, in which a Start of it runs;
    none where no Run allows it.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `alt a Result the role may give`.
    """
    raise NotImplementedError


def pick_up(routes: Sequence[Route], skill: str, kept: Sequence[KeptResult]) -> tuple[Result, ...]:
    """The Results that a Run picked up in a new conversation takes from the Kept results.

    Takes: the Routes, the skill, and the Kept results in the order the run gave them.
    Gives: the Results, each one that a Route after the one before goes after; none where the Kept
    results are none or reach a Route that starts no more, as the run then starts anew.
    Changes: nothing.
    Refuses: OffRoutes, where a Kept result isn't one that the Routes lead to.
    Carries: S7 `alt results that follow the Routes` and `results that don't follow them`.
    """
    raise NotImplementedError
