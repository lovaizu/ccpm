"""start_with: the subagent runs the script its step names before anything else, such as turn's
`scripts/turn.py start`, which gives it what it works from."""

from __future__ import annotations

from collections.abc import Callable

from call import Call, runs

ACTION = "begin"
WORDING = "First run `<script>`."
# Any call may begin the subagent's work, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)
# Its check reads the calls made before, from the record.
RECORD = True


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call is made before the subagent has run a script taken, and runs none itself."""
    return not begun(call, lambda c: runs(c, takes))


def begun(call: Call, by: Callable[[Call], bool]) -> bool:
    """Whether the subagent has begun with what `by` holds a call to, by a call it made before or
    by the call itself, as the guard holds it to run its script first, or to read its part."""
    return any(by(c) for c in [*call.before, call])
