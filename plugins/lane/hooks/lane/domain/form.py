"""The form of Lanes, Routes, adapters, and the Laid, as lanes.json and a Proposal hold them, which
lanes.schema.json beside this file states."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Union

# The values a Lane's type takes, by the names that its type's module gives as `ARGS`, such as the
# `commands` that a run_only Lane allows.
Args = Mapping[str, Union[str, Sequence[str]]]


class OutOfForm(Exception):
    """A lanes.json or a Proposal that lanes.schema.json doesn't take, with each place that's out of
    form and what the form takes there."""

    def __init__(self, problems: Sequence[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = tuple(problems)


@dataclass(frozen=True)
class Lane:
    """A rule of one lane type on one Step: the role whose Step it is, the file and the number of
    the Step, the lane type by its name, and the values its type takes."""

    role: str
    file: str
    step: int
    type: str
    args: Args


@dataclass(frozen=True)
class After:
    """What a Route goes after: the skill's start (`first`), a Result that a role gave (`result`), a
    command that the person types (`command`), or another plugin's run that a move called, once it
    hands its work back (`returned`)."""

    kind: Literal["first", "result", "command", "returned"]
    role: str | None = None
    result: str | None = None
    command: str | None = None
    skill: str | None = None


@dataclass(frozen=True)
class Move:
    """One move that a Route makes due: start a subagent, resume one by SendMessage, wait for the
    person's reply or the command they type, start no more by the skill's own Result, or call
    another plugin's skill."""

    kind: Literal["start", "resume", "wait", "no_more", "call"]
    role: str | None = None
    command: str | None = None
    result: str | None = None
    skill: str | None = None


@dataclass(frozen=True)
class Route:
    """The moves of one skill after what the Route goes after."""

    skill: str
    after: After
    moves: tuple[Move, ...]


@dataclass(frozen=True)
class Adapters:
    """The adapters that lanes.json names, each a path under the plugin's hooks/adapters/: the one
    that gives a start's text, and the one that gives the Kept results."""

    text: str | None
    records: str | None


@dataclass(frozen=True)
class LaidSentence:
    """One sentence that Lane added to a Step, by the Step's file and number."""

    file: str
    step: int
    text: str


@dataclass(frozen=True)
class Laid:
    """What Lane added to the plugin: the version of the Lane that laid it, and each sentence it
    added to a Step. Every version keeps these fields and those of LaidSentence, as a later
    lay.py reads them through the copy of this code that laid them."""

    version: str
    sentences: tuple[LaidSentence, ...]


@dataclass(frozen=True)
class Proposal:
    """The Lanes, the Routes, and the adapters that up proposes for one plugin."""

    lanes: tuple[Lane, ...]
    routes: tuple[Route, ...]
    adapters: Adapters


@dataclass(frozen=True)
class LanesFile:
    """lanes.json: the approved Proposal as laid, and the Laid."""

    proposal: Proposal
    laid: Laid


def proposal_form() -> dict[str, Any]:
    """The form of a Proposal, as a JSON Schema, which lay.py types gives up.

    Takes: nothing.
    Gives: the JSON Schema of a Proposal, taken from lanes.schema.json.
    Changes: nothing.
    Refuses: nothing; a lanes.schema.json that can't be read is a fault of Lane's own folder.
    Carries: S1 `L-->>UP: the types, and the form of a Proposal`.
    """
    raise NotImplementedError


def read_proposal(text: str) -> Proposal:
    """The Proposal that up wrote, read from its JSON.

    Takes: the JSON text of a Proposal, as up hands it to lay.py print.
    Gives: the Proposal.
    Changes: nothing.
    Refuses: OutOfForm, where the text isn't JSON or lanes.schema.json doesn't take it, so that up
    mends the Proposal.
    Carries: S1 `UP->>L: print (Proposal)`.
    """
    raise NotImplementedError


def read_lanes(path: str) -> LanesFile:
    """lanes.json, read in the form of this Lane's code.

    Takes: the path of a plugin's hooks/lanes.json.
    Gives: the Lanes, Routes, adapters, and Laid it holds.
    Changes: nothing.
    Refuses: OutOfForm, where the file isn't in the form, and FileNotFoundError, where it isn't
    there, so that the guard says it can't check and who must fix it.
    Carries: the guard's reading of the Lanes and Routes on each event of S1 to S7, and S4 `L->>LS:
    reads the Laid by the guard's code in its hooks/lane/`, as the plugin's copy of this code
    reads it for a later lay.py.
    """
    raise NotImplementedError


def write_lanes(path: str, lanes: LanesFile) -> None:
    """Writes lanes.json whole, in the form of this Lane's code.

    Takes: the path of the plugin's hooks/lanes.json, and what it is to hold.
    Gives: nothing.
    Changes: the file, replaced at once.
    Refuses: OSError, where the file can't be written, so that lay.py write puts back each file it
    changed.
    Carries: S2 `L->>G: writes lanes.json through the guard's code`.
    """
    raise NotImplementedError
