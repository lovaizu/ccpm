"""Holds a step done once the role has run a command it takes, as a lane of the trace kind."""

from __future__ import annotations

import lanes

WORDING = "Run `<commands>`."
COMMANDS = "commands"
TRACE = True


def traced(call: lanes.Call, given: dict[str, list[str]]) -> bool:
    """Whether the call is a Bash run of one of the commands."""
    return lanes.ran(call, given["commands"])


def done(given: dict[str, list[str]], calls: list[lanes.Call]) -> str | None:
    """What's left to run, or None where a run of one of the commands came back, or where a value
    given as null leaves no command."""
    if not given["commands"] or any(traced(c, given) for c in calls):
        return None
    return f"{lanes.listed(given['commands'])} hasn't run yet."
