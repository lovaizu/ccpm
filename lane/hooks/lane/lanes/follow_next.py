"""follow_next: the subagent takes the move a script its step names printed as its next, such as
turn's `scripts/turn.py next` telling the orchestrator what to do now. The move is read at the move
port, in lane's form the tool call itself, one JSON line `{"tool": ..., "input": {...}}`, a form
general to any plugin. The move is the subagent's next, so the lane is held both on a tool call and as the subagent is
about to end. It is held from the calls the subagent made before: once the script has printed a
move, each call, and the end, is a drift until a call takes it, that tool with each field of the
input printed equal; the fields not printed are free. Where the script printed no move, such as a
result to return, the subagent is free to end."""

from __future__ import annotations

from typing import Any

from call import Call, End, runs
from ports import Port

ACTION = "follow"
WORDING = "Take the next move `<script>` printed."
# Any call may be the move printed, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)
EVENTS = ("PreToolUse", "SubagentStop")
# It reads what the script printed at the move port.
PORT = "move"


def drifts(given: Call | End, takes: list[str], root: str, read: Port) -> bool:
    """Whether the call is made, or the subagent ends, while the move a script taken last printed,
    read at the move port by read, is due, and is not that move: a move no call since took."""
    if isinstance(given, End):
        before, now = given.made or [], None
    else:
        before, now = given.before or [], given
    move = None
    for c in before:
        if runs(c, takes):
            move = read({"output": c.result})["move"]
        elif move is not None and taken(c, move):
            move = None
    return move is not None and (now is None or not taken(now, move))


def taken(call: Call, move: dict[str, Any]) -> bool:
    """Whether the call is the move: its tool, with each field of the move's input given equal."""
    tool, given = move["tool"], move["input"]
    return call.tool == tool and all(
        k in call.given and call.given[k] == v for k, v in given.items()
    )
