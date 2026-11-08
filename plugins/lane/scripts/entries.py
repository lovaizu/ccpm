"""Decides the hook entries that `lay.py` lays in a plugin's `hooks/hooks.json`: one for each event
the guard reads, each running hook.py with the plugin's name, beside the plugin's own entries.

Each entry checks first in `sh` that `python3` is 3.9 or later, as the guard can't even read the
event without it. Where it isn't, the entry of PreToolUse denies each call of a role that the guard
holds, and every other entry lets the event go on.
"""

from __future__ import annotations

import json
from typing import Any

# Each event the guard reads, in the order the entries lie in.
EVENTS = (
    "PreToolUse",
    "PostToolUse",
    "SubagentStart",
    "SubagentStop",
    "UserPromptExpansion",
    "UserPromptSubmit",
    "Stop",
)
# The events whose entries match every tool or every subagent's type.
MATCHED = ("PreToolUse", "PostToolUse", "SubagentStart", "SubagentStop")
# Where each entry that Lane lays runs Lane's code. Lane laid each hook whose command names
# `/hooks/lane/`. Its form may be an earlier one.
MARK = "${CLAUDE_PLUGIN_ROOT}/hooks/lane/"
# The most seconds an entry runs, which leaves the guard time to wait for a start and to run an
# adapter.
TIMEOUT = 10
# The check that python3 is 3.9 or later.
PYTHON = 'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'


def laid(name: str, held: tuple[str, ...]) -> dict[str, Any]:
    """The hook entries of the plugin of the name, whose held roles have the agent types given."""
    hooks: dict[str, Any] = {}
    for event in EVENTS:
        hook: dict[str, Any] = {
            "type": "command",
            "timeout": TIMEOUT,
            "command": _command(event, name, held),
        }
        if event == "PreToolUse":
            hook["onFailure"] = "block"
        group: dict[str, Any] = {"hooks": [hook]}
        if event in MATCHED:
            group = {"matcher": "*", **group}
        hooks[event] = [group]
    return {"hooks": hooks}


def _command(event: str, name: str, held: tuple[str, ...]) -> str:
    run = f'exec python3 -B "{MARK}hook.py" {name}'
    if event != "PreToolUse" or not held:
        return f"{PYTHON} || exit 0; {run}"
    told = f"{name}: install Python 3.9 or later, run as python3, for its hooks to run"
    output = {
        "systemMessage": told,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": told,
        },
    }
    cases = "|".join(f'*\'"agent_type":"{t}"\'*|*\'"agent_type": "{t}"\'*' for t in held)
    fallback = f"case \"$(cat)\" in {cases}) echo '{json.dumps(output)}';; esac; exit 0"
    return f"{PYTHON} || {{ {fallback}; }}; {run}"


def _lanes(group: dict[str, Any]) -> bool:
    """Whether the group of hooks is one that Lane laid, now or in an earlier form."""
    return any("/hooks/lane/" in h.get("command", "") for h in group.get("hooks", []))


def merged(existing: dict[str, Any] | None, name: str, held: tuple[str, ...]) -> dict[str, Any]:
    """The plugin's hook entries with Lane's laid anew: each entry of its own kept in its place,
    and each entry that Lane laid before replaced."""
    hooks: dict[str, Any] = {}
    for event, groups in ((existing or {}).get("hooks") or {}).items():
        own = [g for g in groups if not _lanes(g)]
        if own:
            hooks[event] = own
    for event, groups in laid(name, held)["hooks"].items():
        hooks[event] = hooks.get(event, []) + groups
    return {**(existing or {}), "hooks": hooks}


def current(existing: dict[str, Any] | None, name: str, held: tuple[str, ...]) -> bool:
    """Whether the plugin's hook entries hold Lane's as `laid` gives them now, and no other."""
    return existing is not None and merged(existing, name, held) == existing
