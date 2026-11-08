"""Puts each command it takes to the person before the command runs, through Claude Code's own
permission prompt."""

from __future__ import annotations

import lanes

WORDING = "Run `<commands>` only with the person's approval."
COMMANDS = "commands"


def held(call: lanes.Call, given: dict[str, list[str]]) -> bool:
    """Whether the call is a Bash run of one of the commands, which goes to the person."""
    return lanes.ran(call, given["commands"])
