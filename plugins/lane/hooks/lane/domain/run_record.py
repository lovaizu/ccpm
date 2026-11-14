"""Decides where the run record of a conversation lies, and how its Run, with each Start, Call, and
Result, is written to it and read back, so that the guard and result.py decide each move from the
record and never from the conversation, as the principle The run kept in a file says."""

from __future__ import annotations

from dataclasses import dataclass, field

from domain.event import Call
from domain.laid_set import Move

# Who called the skill that the Run runs.
PERSON, AI = "person", "ai"


@dataclass
class Start:
    """One start of a role that a Route made due, the data model's Start: `number` its place in the
    Run, from 1; `role`; `text` the text passed word for word; `values` the run values that the
    adapter gave beside it; `agent` the ID of the subagent it started, "" until Claude Code names
    it; `running` whether that subagent runs; `resumes` the number of the Start whose subagent a
    resume that a Route lists starts again, or 0 for a first start."""

    number: int
    role: str
    text: str
    values: dict[str, str] = field(default_factory=dict)
    agent: str = ""
    running: bool = False
    resumes: int = 0


@dataclass
class Result:
    """One result given by result.py, the data model's Result: the role, the result, the ID of the
    subagent that ran result.py, "" for the main conversation, and the number of its Start, 0 for
    the skill's own."""

    role: str
    result: str
    agent: str = ""
    start: int = 0


@dataclass
class Run:
    """One run of a plugin's skill in one conversation, the data model's Run: the plugin, its
    skill, the conversation's ID, who called the skill, PERSON or AI, each Start, Call, and Result
    in order, the moves open, the text and the values that the adapter gave for each role whose
    start the moves open, the lines that a Lane's command printed for each subagent since its
    Start, and whether the Run ended. A Run of Lane's up keeps, besides, what `lay.py print` showed
    last, and whether the person typed a prompt since then."""

    plugin: str
    skill: str
    session: str
    by: str
    starts: list[Start] = field(default_factory=list)
    calls: list[tuple[str, Call]] = field(default_factory=list)
    results: list[Result] = field(default_factory=list)
    moves: list[Move] = field(default_factory=list)
    texts: dict[str, tuple[str, dict[str, str]]] = field(default_factory=dict)
    printed: dict[str, list[str]] = field(default_factory=dict)
    ended: bool = False
    shown: str = ""
    prompted: bool = False


def path(temp: str, plugin: str, session: str) -> str:
    """The run record of the plugin's Run in the conversation: `<temp>/<plugin>/<yyyymmdd>-<the
    conversation's ID>/run.jsonl`, `<yyyymmdd>` the day the conversation's first Run started, as the
    plugin guide places what a plugin uses only while it runs. The same plugin and conversation give
    the same file on a later day."""
    raise NotImplementedError("run_record.path")


def dumps(run: Run) -> str:
    """The Run as the JSON Lines of its run record, which `loads` reads back equal to it."""
    raise NotImplementedError("run_record.dumps")


def loads(text: str, where: str) -> Run:
    """The Run of the text of the run record at `where`. Raises Fault, naming the file, with Lane to
    fix it, where the text isn't a Run."""
    raise NotImplementedError("run_record.loads")


def load(temp: str, plugin: str, session: str) -> Run | None:
    """The plugin's Run in the conversation, as its run record holds it, ended or not, or None
    where the conversation has none. Raises Fault as `loads` does."""
    raise NotImplementedError("run_record.load")


def save(run: Run, temp: str) -> None:
    """Writes the Run to its run record whole, so that a reader never meets half of it, making its
    folder where it isn't there."""
    raise NotImplementedError("run_record.save")
