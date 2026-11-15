"""The run record's layout: where the record of one conversation lies in the system's temporary
folder, and the form of each line, added once and never rewritten, holding only what no later
payload gives again."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, Union


class Unreadable(Exception):
    """A run record that can't be read, or holds a line out of its form, with where, so that the
    guard says it can't check and who must fix it."""


@dataclass(frozen=True)
class Called:
    """The call of a skill that starts a Run, by a person or an AI, with the words typed after
    it."""

    run: str
    skill: str
    by: Literal["person", "ai"]
    words: str


@dataclass(frozen=True)
class Prompted:
    """A prompt typed in a Run, which the Data model's Run holds, such as a reply or a command that
    a Route waits for or goes after."""

    run: str
    text: str


@dataclass(frozen=True)
class Shown:
    """What lay.py print showed in up's Run, with the Proposal's ID."""

    run: str
    proposal_id: str
    words: str


@dataclass(frozen=True)
class Started:
    """A Start that the guard let through: its role, its text and run values, the Agent or
    SendMessage call that made it, and whether it resumes a subagent."""

    run: str
    role: str
    text: str
    values: Mapping[str, str]
    tool_use_id: str
    resumed: bool


@dataclass(frozen=True)
class Tied:
    """The tie of a Start, by its call, to the subagent's agent_id, made at the call's
    PostToolUse."""

    run: str
    tool_use_id: str
    agent_id: str


@dataclass(frozen=True)
class Gave:
    """A Result given by result.py: the role or skill, the Result, and the subagent's agent_id, None
    where the main conversation gave it."""

    run: str
    role: str
    result: str
    agent_id: str | None


@dataclass(frozen=True)
class Ended:
    """A subagent's end as it reached the main conversation, and whether TaskStop stopped it."""

    run: str
    agent_id: str
    killed: bool


@dataclass(frozen=True)
class SteppedAside:
    """The main conversation's call of another plugin's skill that a move names, which sets the Run
    aside until the move after it."""

    run: str
    skill: str


Line = Union[Called, Prompted, Shown, Started, Tied, Gave, Ended, SteppedAside]


def record_path(plugin: str, session_id: str) -> str:
    """Where the run record of one conversation lies.

    Takes: the plugin's name, and the conversation's session_id.
    Gives: the path of `<plugin>/<yyyymmdd>-<session_id>/` in the system's temporary folder, with
    the record's file in it, the day being the one the record was first written on.
    Changes: nothing.
    Refuses: nothing.
    Carries: where each `G->>RS` arrow of S1 to S7 reaches, and S2 `G->>RS: reads the lines`.
    """
    raise NotImplementedError("run_record.record_path")


def add(path: str, line: Line) -> None:
    """Adds one line to the end of the run record.

    Takes: the record's path, and the line.
    Gives: nothing.
    Changes: the record, one line appended, its folder made where it isn't there.
    Refuses: OSError, where the record can't be written, so that the guard stops the event's call
    with why.
    Carries: each `G->>RS: adds ...` arrow of S1 to S7.
    """
    raise NotImplementedError("run_record.add")


def lines(path: str) -> tuple[Line, ...]:
    """Each line of the run record, in the order added.

    Takes: the record's path.
    Gives: its lines, none where the record isn't there yet.
    Changes: nothing.
    Refuses: Unreadable.
    Carries: S2 `G->>RS: reads the lines`, S6 `G->>RS: reads the lines, for its Start and Run`.
    """
    raise NotImplementedError("run_record.lines")
