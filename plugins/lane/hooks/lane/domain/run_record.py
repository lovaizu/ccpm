"""The run record's layout: where the record of one conversation lies in the system's temporary
folder, and the form of each line, added once and never rewritten, holding only what no later
payload gives again."""

from __future__ import annotations

import dataclasses
import datetime
import glob
import json
import os
import tempfile
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
class Marked:
    """A Mark given by step.py or item.py that gave 0: the role or skill, the Step it marks, or for
    an Item the Step due as it was marked, the Item's ID, None for a Step's Mark, and the
    subagent's agent_id, None where the main conversation gave it."""

    run: str
    role: str
    step: int
    item: str | None
    agent_id: str | None


@dataclass(frozen=True)
class Read:
    """A Read of a path that a Lane of reads_whole names, as its PostToolUse gave it: the role or
    skill, the path as the Lane names it with the run values filled in, the first and the last
    line it read, and the subagent's agent_id, None where the main conversation read it."""

    run: str
    role: str
    path: str
    first: int
    last: int
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


@dataclass(frozen=True)
class TextFailed:
    """The adapter of a start's text, failed at the skill's call, so that the guard asks it again
    after each later call of the main conversation, as the skill's own steps may make what it
    reads."""

    run: str


@dataclass(frozen=True)
class TextGiven:
    """The adapter of a start's text, which failed at the skill's call, answering at a later call,
    so that the guard has given each start due with its text and asks it no more."""

    run: str


Line = Union[
    Called,
    Prompted,
    Shown,
    Started,
    Tied,
    Gave,
    Marked,
    Read,
    Ended,
    SteppedAside,
    TextFailed,
    TextGiven,
]
# What a role did on its Steps that the record keeps, in the order added: each Mark and each Read.
Report = Union[Marked, Read]
# Each kind of line, by the name that a line of the record gives as its `kind`.
_KINDS = {
    kind.__name__: kind
    for kind in (
        Called,
        Prompted,
        Shown,
        Started,
        Tied,
        Gave,
        Marked,
        Read,
        Ended,
        SteppedAside,
        TextFailed,
        TextGiven,
    )
}
# The file of the record in its conversation's folder.
RECORD = "record.jsonl"


def record_path(plugin: str, session_id: str) -> str:
    """Where the run record of one conversation lies.

    Takes: the plugin's name, and the conversation's session_id.
    Gives: the path of `<plugin>/<yyyymmdd>-<session_id>/` in the system's temporary folder, with
    the record's file in it, the day being the one the record was first written on.
    Changes: nothing.
    Refuses: nothing.
    Carries: where each `G->>RS` arrow of S1 to S7 reaches, and S2 `G->>RS: reads the lines`.
    """
    plugin_folder = os.path.join(tempfile.gettempdir(), plugin)
    begun = sorted(
        glob.glob(os.path.join(glob.escape(plugin_folder), f"*-{glob.escape(session_id)}"))
    )
    day = datetime.date.today().strftime("%Y%m%d")
    folder = begun[0] if begun else os.path.join(plugin_folder, f"{day}-{session_id}")
    return os.path.join(folder, RECORD)


def add(path: str, line: Line) -> None:
    """Adds one line to the end of the run record.

    Takes: the record's path, and the line.
    Gives: nothing.
    Changes: the record, one line appended, its folder made where it isn't there.
    Refuses: OSError, where the record can't be written, so that the guard stops the event's call
    with why.
    Carries: each `G->>RS: adds ...` arrow of S1 to S7.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    held = {"kind": type(line).__name__, **dataclasses.asdict(line)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(held) + "\n")


def lines(path: str) -> tuple[Line, ...]:
    """Each line of the run record, in the order added.

    Takes: the record's path.
    Gives: its lines, none where the record isn't there yet.
    Changes: nothing.
    Refuses: Unreadable.
    Carries: S2 `G->>RS: reads the lines`, S6 `G->>RS: reads the lines, for its Start, its Marks,
    and its Run`.
    """
    if not os.path.exists(path):
        return ()
    with open(path, encoding="utf-8") as f:
        return tuple(_line(path, number, text) for number, text in enumerate(f, 1))


def _line(path: str, number: int, text: str) -> Line:
    """One line of the record, read into its kind."""
    try:
        held = json.loads(text)
        return _KINDS[held.pop("kind")](**held)
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        raise Unreadable(f"{path}, line {number}: not a line of the run record: {e}") from e
