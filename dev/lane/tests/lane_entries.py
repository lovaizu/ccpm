"""How Lane's unit cases write the entries of a run r1 in the run record, in the form that
hooks/lane/record.py gives them, for the entries that more than one interface's cases hold."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from record import Entry


def start(use: str, role: str = "log:writer", prompt: str = "You are log:writer.") -> Entry:
    """A start of the role by the call `use`, with the prompt that the main conversation gave
    it."""
    return {"kind": "start", "run": "r1", "role": role, "tool_use_id": use, "prompt": prompt}


def tie(use: str, agent_id: str) -> Entry:
    """The start of the call `use` tied to the subagent."""
    return {"kind": "tie", "run": "r1", "tool_use_id": use, "agent_id": agent_id}


def result(agent_id: str, value: str, role: str = "log:writer") -> Entry:
    """The result that the subagent of the role gave."""
    return {"kind": "result", "run": "r1", "agent_id": agent_id, "role": role, "result": value}


def read(agent_id: str | None, path: str, first: int, last: int) -> Entry:
    """The subagent's read of the file at the path, from its line `first` to its line `last`, or the
    main conversation's for None."""
    return {
        "kind": "read",
        "run": "r1",
        "agent_id": agent_id,
        "path": path,
        "first_line": first,
        "last_line": last,
    }
