"""follow_next: the subagent takes the move a script its step names printed as its next, such as
turn's `scripts/turn.py next` telling the orchestrator what to do now. The script prints the move as
the tool call itself, one JSON line `{"tool": ..., "input": {...}}`, a form general to any plugin.
The move is the subagent's next, so the lane is held both on a tool call and as the subagent is
about to end. It is held from the calls the subagent made before: once the script has printed a
move, each call, and the end, is a drift until a call takes it, that tool with each field of the
input printed equal; the fields not printed are free. Where the script printed no move, such as a
result to return, the subagent is free to end."""

from __future__ import annotations

from typing import Any

import started
from call import Call, End, runs

ACTION = "follow"
WORDING = "Take the next move `<script>` printed."
# Any call may be the move printed, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)
EVENTS = ("PreToolUse", "SubagentStop")
# Its check reads the calls made before, from the record, on a tool call too.
RECORD = True


def drifts(given: Call | End, takes: list[str], root: str) -> bool:
    """Whether the call is made, or the subagent ends, while the move a script taken last printed
    is due, and is not that move: a move no call since took."""
    if isinstance(given, End):
        before, now = given.made or [], None
    else:
        before, now = given.before or [], given
    move = None
    for c in before:
        if runs(c, takes):
            move = printed(c.result)
        elif move is not None and taken(c, move):
            move = None
    return move is not None and (now is None or not taken(now, move))


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
