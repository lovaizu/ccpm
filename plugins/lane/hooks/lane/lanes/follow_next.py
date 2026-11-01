"""follow_next: the subagent takes each move a script its step names prints, and runs the script
again after each, until it prints none, such as a plugin's `scripts/next.py` telling the subagent
what to do now. The move is read at the move port, in lane's form the tool call itself, one JSON
line `{"tool": ..., "input": {...}}`, a form general to any plugin. The move is the subagent's next,
so the lane is held both on a tool call and as the subagent is about to end. It is held from the
calls the subagent made before: ending before the script's first run is a drift, each call before
it free; once the script has printed a move, each call, and the end, is a drift until a call takes
it, that tool with each field of the input printed equal, the fields not printed free; once the
move is taken, each call, and the end, is a drift until the script runs again. A run of the script
is never a drift, and a run that failed, exiting other than 0, changes nothing of what is due of
the calls, and lets the subagent end, so its report of the failure reaches whoever started it.
Once the script's last run printed no move, such as a result to return, the subagent is free."""

from __future__ import annotations

from typing import Any

from call import Call, End, runs
from ports import Port

ACTION = "follow"
WORDING = "Take each move `<script>` prints, until it prints none."
# Any call may be the move printed, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)
EVENTS = ("PreToolUse", "SubagentStop")
# It reads what the script printed at the move port.
PORT = "move"


def drifts(given: Call | End, takes: list[str], root: str, read: Port) -> bool:
    """Whether the call is made, or the subagent ends, while something is due and the call is not
    it: a move the script taken last printed, read at the move port by read, that no call since
    took, or, once a call took it, a run of the script again; or whether the subagent ends before
    the script's first run. The end is free once the script's last run failed."""
    if isinstance(given, End):
        before, now = given.made, None
    else:
        before, now = given.before, given
    if now is not None and runs(now, takes):
        return False
    move, again, last = None, False, None
    for c in before:
        if runs(c, takes):
            last = c
            if not c.failed:
                move, again = read({"output": c.result})["move"], False
        elif move is not None and taken(c, move):
            move, again = None, True
    if now is None:
        return last is None or (not last.failed and (again or move is not None))
    return again or (move is not None and not taken(now, move))


def taken(call: Call, move: dict[str, Any]) -> bool:
    """Whether the call is the move: its tool, with each field of the move's input given equal."""
    tool, given = move["tool"], move["input"]
    return call.tool == tool and all(
        k in call.given and call.given[k] == v for k, v in given.items()
    )
