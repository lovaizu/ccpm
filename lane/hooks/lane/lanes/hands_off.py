"""hands_off: the subagent does not run the commands its step names, such as `git commit` held for
the orchestrator once the user has read the work."""

from __future__ import annotations

from call import Call

ACTION = "run"
WORDING = "Do not run `<commands>`."
TOOLS = ("Bash",)


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call runs one of the commands taken: a command of the call whose words begin
    with the command's words, so `git commit` holds `git commit -m m` and not `git commit-tree`."""
    commands = [c.split() for c in takes]
    return call.action == ACTION and any(
        words[: len(c)] == c for words in call.what for c in commands
    )
