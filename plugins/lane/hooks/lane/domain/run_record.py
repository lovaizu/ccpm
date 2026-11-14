"""Decides where the run record of a conversation lies, which facts it keeps, and the form of each
line: it keeps only the facts that no later payload of Claude Code gives again, each as a line that
a hook adds and never rewrites, as the hooks of subagents that run side by side run at once. The
guard works out where each Run stands from these lines on each event, as `routes.stand` does, so
that it decides each move from the record and never from the conversation, as the principle The run
kept in a file says. What a payload carries each time, such as the conversation's ID, a subagent's
type, or the skill that a result names, the record never keeps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from domain.laid_set import Move

# Who called the skill that a Run runs.
PERSON, AI = "person", "ai"

# What a Noted line tells.
ENDED = "ended"  # a subagent's end reached the main conversation, its status in `text`
TYPED = "typed"  # the person typed a command that a Route waits for or goes after, in `text`
PRINTED = "printed"  # a command that a Lane checks the end against printed the line in `text`
SHOWN = "shown"  # `lay.py print` showed the text in `text`, in a Run of up
PROMPTED = "prompted"  # the person typed a prompt, in a Run of up
TURN_ENDED = "turn_ended"  # the main conversation's turn ended, in a Run of up
LAID = "laid"  # `lay.py write` laid a Proposal, in a Run of up


@dataclass(frozen=True)
class Called:
    """A line: the skill of the plugin was called, which begins its Run, by PERSON or AI."""

    skill: str
    by: str


@dataclass(frozen=True)
class Start:
    """One start of a role that a Route made due, the data model's Start: `number` its place among
    the conversation's Starts, from 1; `role`; `text` the text passed word for word; `values` the
    run values that the adapter gave beside it; `resumes` the number of the Start whose subagent a
    resume that a Route lists starts again, or 0 for a first start; and `skill` the skill whose Run
    made it due. Its line holds these alone. `agent`, the ID of the subagent it started, and
    `running`, whether that subagent runs, are worked out from the Tied and Noted lines, never kept
    in its line."""

    number: int
    role: str
    text: str
    values: dict[str, str] = field(default_factory=dict)
    agent: str = ""
    running: bool = False
    resumes: int = 0
    skill: str = ""


@dataclass(frozen=True)
class Tied:
    """A line: the PostToolUse of the Start's Agent call named the subagent `agent` it started."""

    start: int
    agent: str


@dataclass(frozen=True)
class Result:
    """One result given by a run of result.py, the data model's Result: the role, the result, and
    the ID of the subagent that ran result.py, "" for the main conversation. Its line holds these
    alone. `start`, the number of the Start that the subagent's tie names, 0 for a skill's own, is
    worked out, never kept in its line."""

    role: str
    result: str
    agent: str = ""
    start: int = 0


@dataclass(frozen=True)
class Noted:
    """A line of each other fact that one event alone tells: `what` one of ENDED to LAID, `agent`
    the subagent it's of, "" for the main conversation, and `text` what it holds."""

    what: str
    agent: str = ""
    text: str = ""


# Python 3.9, which the laid plugin runs on, has no `|` between classes.
Line = Union[Called, Start, Tied, Result, Noted]


@dataclass
class Run:
    """One run of one skill of a plugin in one conversation, the data model's Run, as `routes.stand`
    works it out from the lines of the run record and never written whole: the plugin, its skill,
    the conversation's ID, who called the skill, PERSON or AI, each Start and Result of the Run in
    order, the moves open, the lines that a Lane's command printed for each subagent since its
    Start, and whether the Run ended. A Run of Lane's up holds, besides, what `lay.py print` showed
    last, and whether the person typed a prompt since then."""

    plugin: str
    skill: str
    session: str
    by: str
    starts: list[Start] = field(default_factory=list)
    results: list[Result] = field(default_factory=list)
    moves: list[Move] = field(default_factory=list)
    printed: dict[str, list[str]] = field(default_factory=dict)
    ended: bool = False
    shown: str = ""
    prompted: bool = False


def path(temp: str, plugin: str, session: str) -> str:
    """The run record of the plugin in the conversation, which holds the lines of each skill's Run:
    `<temp>/<plugin>/<yyyymmdd>-<the conversation's ID>/run.jsonl`, `<yyyymmdd>` the day the
    conversation's first Run began, as the plugin guide places what a plugin uses only while it
    runs. The same plugin and conversation give the same file on a later day."""
    raise NotImplementedError("run_record.path")


def dumps(line: Line) -> str:
    """The line as one line of JSON, ending with a newline, which `loads` reads back equal to it."""
    raise NotImplementedError("run_record.dumps")


def loads(text: str, where: str) -> tuple[Line, ...]:
    """Each line of the text of the run record at `where`, in order. Raises Fault, naming the file
    and the line, with Lane to fix it, where a line isn't one that `dumps` writes. A last line cut
    short by a hook that still writes is left out."""
    raise NotImplementedError("run_record.loads")


def load(temp: str, plugin: str, session: str) -> tuple[Line, ...]:
    """Each line of the plugin's run record in the conversation, none where the conversation has
    none. Raises Fault as `loads` does."""
    raise NotImplementedError("run_record.load")


def add(line: Line, temp: str, plugin: str, session: str) -> None:
    """Adds the line at the end of the plugin's run record in the conversation, in one write, so
    that a hook that runs at the same time never loses it or another's, making its folder where it
    isn't there. It never rewrites a line."""
    raise NotImplementedError("run_record.add")
