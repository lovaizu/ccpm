"""run_step: a lane of the trace kind, whose step the subagent has done once a command it names, one
of them, came back in this start: a Bash call of it, matched whole as run_only matches a command,
each value the start's own, kept as it came back, as lane keeps no call that failed."""

from __future__ import annotations

from lanes import run_only
from lanes.done import Done

ACTION = "run"
WORDING = "Run `<commands>`."
CALLS = True
TRACE = True


def traces(tool: str, value: str, given: dict[str, list[str]], done: Done) -> bool:
    """Whether a call of the tool on the value, the field of its input a lane judges, is the trace
    of the lane taking the things given: a Bash call of one of its commands."""
    return tool == "Bash" and run_only.allows(
        value, given["commands"], done.root, done.cwd, done.values
    )


def missing(given: dict[str, list[str]], done: Done) -> str:
    """What's missing: that none of the commands came back in this start; "" where one did."""
    for c in done.run:
        command = str(c.get("input", {}).get("command", ""))
        if traces(str(c.get("tool", "")), command, given, done):
            return ""
    return f"{' or '.join(f'`{t}`' for t in given['commands'])} not run"
