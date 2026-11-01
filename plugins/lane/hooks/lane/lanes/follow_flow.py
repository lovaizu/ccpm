"""follow_flow: the orchestrator of a flow takes each move lane tells it, until lane tells none, as
lane's docs/flow.md says. The layer lays it from the flow, on the orchestrator's step the flow
names, and the guard tells the orchestrator each move as it starts and as each call of a subagent of
the flow comes back. The lane holds it to the move due, read from the flow and its calls kept, as
moves.py reads it: while a move is due, each call but the move, and the end, is a drift, told with
the move on the next line; once the flow is done, the orchestrator is free."""

from __future__ import annotations

from call import Call, End
from moves import Run, due, taken, told

ACTION = "follow"
WORDING = "Take each move lane tells you, until it tells none."
# The lane takes nothing: what it holds is the flow, beside the lanes laid.
MOST = 0
# Any call may come before the move, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)
EVENTS = ("PreToolUse", "SubagentStop")
# Its check is given, fourth, the run of the flow.
FLOW = True


def drifts(given: Call | End, takes: list[str], root: str, run: Run) -> str:
    """The line telling the move due where the call is not that move, or the orchestrator ends,
    while a move is due; "" otherwise."""
    if due(run).at is None or isinstance(given, Call) and taken(run, given):
        return ""
    return told(run)
