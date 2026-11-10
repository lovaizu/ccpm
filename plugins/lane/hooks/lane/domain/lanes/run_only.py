"""run_only: a role runs only the commands its rule names, each matched whole."""

from __future__ import annotations

ACTION = "run"
"""The action the rule watches, as lay.py print names it beside the sentence."""


def sentence(takes: list[str]) -> str:
    """The sentence laid at the end of the step: `Run only `a` or `b`.`, for takes that `refused`
    finds nothing in."""
    return "Run only " + " or ".join(f"`{command}`" for command in takes) + "."


def refused(takes: list[str]) -> str:
    """What's wrong with the takes, or "" where the rule can take them."""
    if not takes:
        return "run_only takes at least one command"
    if any(not command.strip() for command in takes):
        return "run_only takes no blank command"
    if any("`" in command for command in takes):
        return "run_only takes no command with a backtick, as its sentence names each in backticks"
    return ""


def allows(command: str, takes: list[str]) -> bool:
    """Whether the command is one of the takes word for word, blanks at its ends aside. A command
    taken apart by the shell's grammar would let through forms that no one foresaw."""
    return command.strip() in takes
