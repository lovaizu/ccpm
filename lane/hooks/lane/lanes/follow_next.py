"""follow_next: the subagent takes the move a script its step names printed as its next, such as
turn's `scripts/turn.py next` telling the orchestrator what to do now. The script prints the move as
the tool call itself, one JSON line `{"tool": ..., "input": {...}}`, a form general to any plugin.
It is held from the calls the subagent made before: once the script has printed a move, each call is
a drift until one takes it, that tool with each field of the input printed equal; the fields not
printed are free."""

from __future__ import annotations

import json
from typing import Any

from call import Call

from lanes.start_with import runs

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
    """The move in what the script printed: its last line that is a JSON object of a tool's name and
    an input object; None where no line is."""
    for line in reversed(output.splitlines()):
        try:
            move = json.loads(line)
        except ValueError:
            continue
        tool = move.get("tool") if isinstance(move, dict) else None
        given = move.get("input") if isinstance(move, dict) else None
        if isinstance(tool, str) and isinstance(given, dict):
            return tool, given
    return None


def taken(call: Call, move: tuple[str, dict[str, Any]]) -> bool:
    """Whether the call is the move: its tool, with each field of the move's input given equal."""
    tool, given = move
    return call.tool == tool and all(
        k in call.given and call.given[k] == v for k, v in given.items()
    )
