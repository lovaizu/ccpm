"""run_only: the subagent runs no command but those its step names, each matched whole, as the
Bash tool's input gives it, and no part of it read."""

from __future__ import annotations

# What Claude Code puts the plugin's folder in for, in a subagent's file, before the subagent reads
# it.
ROOT = "${CLAUDE_PLUGIN_ROOT}"

ACTION = "run"
WORDING = "Run only `<commands>`."


def named(takes: list[str], root: str) -> list[str]:
    """The commands taken, as the subagent reads them in its step: the plugin's folder put in where
    a command names ROOT."""
    return [t.replace(ROOT, root) for t in takes]


def allows(command: str, takes: list[str], root: str, cwd: str) -> bool:
    """Whether the command is one of those taken, whole, as the subagent reads them, the blanks
    around it left out, as a model may end a command with a line break."""
    return command.strip() in named(takes, root)
