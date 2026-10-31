"""hands_off: the subagent does not run the commands its step names, such as `git commit` held for
the orchestrator once the user has read the work."""

from __future__ import annotations

from call import Call, runs

ACTION = "run"
WORDING = "Do not run `<commands>`."
TOOLS = ("Bash",)


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call runs one of the commands taken."""
    return runs(call, takes)
