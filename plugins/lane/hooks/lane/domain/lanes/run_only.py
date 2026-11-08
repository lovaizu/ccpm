"""Holds a role's commands to those that its lanes name."""

from __future__ import annotations

import command

import lanes

WORDING = "Run only `<commands>`."
COMMANDS = "commands"


def check(call: lanes.Call, given: dict[str, list[str]], context: lanes.Context) -> str | None:
    """What the role may run, where the call is a Bash command that no lane of the role names, or
    None where the call goes on.

    It raises `lanes.Malformed` where the Bash call gives no command.
    """
    if call.tool != "Bash":
        return None
    run = call.input.get("command")
    if not isinstance(run, str):
        raise lanes.Malformed("the Bash call gives no command")
    if any(command.matches(run, c) for c in context.commands):
        return None
    if not context.commands:
        return "You may run no command."
    quoted = [f"`{c}`" for c in context.commands]
    joined = quoted[0] if len(quoted) == 1 else ", ".join(quoted[:-1]) + " and " + quoted[-1]
    lines = [f"The commands you may run: {joined}."]
    for name in dict.fromkeys(n for c in context.commands for n in command.dependencies(c)):
        lines.append(
            f"`${{dependency:{name}}}` stands for the folder that holds the plugin {name}."
        )
    return "\n".join(lines)
