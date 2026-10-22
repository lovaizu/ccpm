"""hands_off: the subagent does not run the commands its step names, such as `git commit` held for
the orchestrator once the builder has read the work."""

from __future__ import annotations

from call import Call

ACTION = "run"
WORDING = "Do not run `<commands>`."
TOOLS = ("Bash",)


def drifts(call: Call, takes: list[str]) -> bool:
    """Whether the call runs one of the commands taken: a command of the call whose words begin
    with the command's words, so `git commit` holds `git commit -m m` and not `git commit-tree`."""
    commands = [c.split() for c in takes]
    # Told by membership rather than `==`, as an order comparison such as `<=` would tell this
    # action from others too, and a mutant making it one would pass every test.
    return call.action in (ACTION,) and any(
        words[: len(c)] == c for words in call.what for c in commands
    )
