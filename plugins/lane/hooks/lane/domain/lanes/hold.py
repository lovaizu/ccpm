"""hold: a command its step names is run only with the person's approval: lane answers Claude Code
to ask the person, with the sentence, and Claude Code's permission prompt puts it to them. Each
command is matched whole, as run_only matches it."""

from __future__ import annotations

from lanes import run_only

ACTION = "run"
WORDING = "Run `<commands>` only with the person's approval."
CALLS = False


def allows(command: str, takes: list[str], root: str, cwd: str) -> bool:
    """Whether the command is one of those held, whole, as the subagent reads them."""
    return run_only.allows(command, takes, root, cwd)
