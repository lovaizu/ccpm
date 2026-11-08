"""Holds a role's end until a test it takes has passed after the last change of its output."""

from __future__ import annotations

import lanes

WORDING = "After changing `<output>`, pass `<test>`."
COMMANDS = "test"
END = True


def end(given: dict[str, list[str]], calls: list[lanes.Call], context: lanes.Context) -> str | None:
    """What's missing, where a write of the output came after the last test that passed, or None.

    A test passed where its run came back, as Claude Code gives PostToolUse only to a command that
    exits with no error. A test given as null leaves no test to pass.
    """
    if not given["test"]:
        return None
    changed = passed = -1
    for index, call in enumerate(calls):
        if lanes.writes(call, given["output"]):
            changed = index
        if lanes.ran(call, given["test"]):
            passed = index
    if changed < 0 or passed > changed:
        return None
    return (
        f"{lanes.listed(given['output'])} changed after the last pass of"
        f" {lanes.listed(given['test'])}."
    )
