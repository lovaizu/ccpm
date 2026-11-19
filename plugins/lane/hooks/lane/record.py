"""The layout of the run record, a file of each conversation in the system temp folder that only
grows, holding only what no later move gives again, so a run's folder found after the run is added
is a line of its own."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


class Entry(TypedDict, total=False):
    """One line of the run record: its `kind`, one of `run`, `folder`, `start`, `tie`, `queue`,
    `drop`, `read`, `mark`, `result`, `stopped`, and `typed`, the `run` it belongs to, and the
    fields of that kind: a `folder` gives the run's plugin's folder, a `queue` a resume queued to a
    subagent that still runs, untied until that subagent's SubagentStop, and a `stopped` the
    `agent_id` of a start that ended with no result, such as one stopped by TaskStop."""

    kind: str
    run: str
    plugin_root: str
    skill: str
    words: str
    role: str
    tool_use_id: str
    agent_id: str
    path: str
    first_line: int
    last_line: int
    step: str
    item: str
    result: str
    command: str


@dataclass
class Run:
    """One run of a plugin's skill in a conversation, from the words typed after its command, with
    its plugin's folder, None until a `folder` entry gives it, and each entry of it in its order."""

    id: str
    session_id: str
    skill: str
    words: str
    plugin_root: str | None = None
    entries: list[Entry] = field(default_factory=list)


def runs(session_id: str) -> list[Run]:
    """Where each run of the conversation stands.

    Takes: the conversation's `session_id`.
    Gives: each run that the record of the conversation holds, with its folder from its `folder`
    entry, and its entries in the order they were added; none where the conversation has no record
    yet.
    Changes: nothing.
    Refuses: OSError, where the record can't be read.
    """
    raise NotImplementedError("record.runs")


def add(session_id: str, entries: list[Entry]) -> None:
    """Adds the entries to the record of the conversation, at its end, in one write.

    Takes: the conversation's `session_id`, and the entries, such as a new run with no folder at
    the skill's call, or a run's folder with each result that follows its routes.
    Gives: nothing.
    Changes: the record of the conversation in the system temp folder, made where it's missing.
    Refuses: OSError, where the record can't be written.
    """
    raise NotImplementedError("record.add")
