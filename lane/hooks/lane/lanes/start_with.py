"""start_with: the subagent runs the script its step names before anything else, such as turn's
`scripts/turn.py start`, which gives it what it works from."""

from __future__ import annotations

from call import Call, runs

ACTION = "begin"
WORDING = "First run `<script>`."
# Any call may begin the subagent's work, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call is made before the subagent has run a script taken, and runs none itself;
    never where what it did before is not known, as a stop then would hold even once the script
    has run."""
    if call.before is None:
        return False
    return not any(runs(c, takes) for c in [*call.before, call])
