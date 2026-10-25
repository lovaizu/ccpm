"""follow_next: the subagent takes the move a script its step names printed as its next, such as
turn's `scripts/turn.py next` telling the orchestrator what to do now. The script prints the move as
the tool call itself, one JSON line `{"tool": ..., "input": {...}}`, a form general to any plugin.
It is held from the calls the subagent made before: once the script has printed a move, each call is
a drift until one takes it, that tool with each field of the input printed equal; the fields not
printed are free."""

from __future__ import annotations

from typing import Any

import started
from call import Call, runs

ACTION = "follow"
WORDING = "Take the next move `<script>` printed."
# Any call may be the move printed, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call is not the move a script taken last printed, where no call since took it."""
    move = None
    for c in call.before or []:
        if runs(c, takes):
            move = printed(c.result)
        elif move is not None and taken(c, move):
            move = None
    return move is not None and not taken(call, move)


def printed(output: str) -> tuple[str, dict[str, Any]] | None:
    """The move in what the script printed: the last JSON object it printed, as started.py finds
    them, that holds a tool's name and an input object; None where none does."""
    for move in reversed(started.objects(output)):
        tool, given = move.get("tool"), move.get("input")
        if isinstance(tool, str) and isinstance(given, dict):
            return tool, given
    return None


def taken(call: Call, move: tuple[str, dict[str, Any]]) -> bool:
    """Whether the call is the move: its tool, with each field of the move's input given equal."""
    tool, given = move
    return call.tool == tool and all(
        k in call.given and call.given[k] == v for k, v in given.items()
    )
