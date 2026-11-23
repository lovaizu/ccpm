"""Decides hook.py's input and output, as Claude Code runs it before each Bash command: it denies
a command of rn's makers that deletes, with how to use remove.py, and lets every other call pass,
as only remove.py removes without a permission prompt that stops the run."""

from __future__ import annotations

import json
import os
from typing import Any

from fault import Answer

from hook.bash import deletes

# What the hook gives to let a call pass: 0, with nothing printed.
PASS: Answer = (0, "", "")

# The start of each `agent_type` of rn's subagents, as Claude Code names a plugin's agent
# `<plugin>:<agent>`, such as `rn:generator`.
RN_AGENT = "rn:"

_REASON = (
    "rn's makers remove files only through remove.py, which asks no permission:"
    " python3 {remove} <exact path> [<exact path> ...]. Give each file or folder you made by its"
    " exact path, absolute or from the current folder, one argument each, with no wildcard. It"
    " removes only inside the git work tree that holds the current folder and inside the system's"
    " temporary folder."
)


def main(stdin: bytes, plugin_root: str) -> Answer:
    """The exit code, stdout, and stderr of `hook.py` on the hook's input, with rn's folder at
    `plugin_root`.

    0 with the JSON that denies the call, its reason giving remove.py's command by its absolute
    path, where the input is a Bash call of one of rn's agents whose command deletes, as
    `hook.bash.deletes` holds it. 0 with nothing printed for every other input, one that isn't the
    hook's JSON and a fault of the hook's own among them, as the hook never stops a call on a
    fault of its own."""
    try:
        return decided(stdin, plugin_root)
    except Exception:  # noqa: BLE001 - the hook's own fault lets the call pass.
        return PASS


def decided(stdin: bytes, plugin_root: str) -> Answer:
    """What the hook gives on its input."""
    try:
        called = json.loads(stdin.decode("utf-8"))
    except ValueError:
        return PASS
    if not (isinstance(called, dict) and _rn_deletes(called)):
        return PASS
    reason = _REASON.format(remove=os.path.join(plugin_root, "scripts", "remove.py"))
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    return 0, json.dumps(output) + "\n", ""


def _rn_deletes(called: dict[str, Any]) -> bool:
    """Whether the call is a Bash command of one of rn's agents that deletes."""
    agent = called.get("agent_type")
    given = called.get("tool_input")
    command = given.get("command") if isinstance(given, dict) else None
    return (
        isinstance(agent, str)
        and agent.startswith(RN_AGENT)
        and called.get("tool_name") == "Bash"
        and isinstance(command, str)
        and deletes(command)
    )
