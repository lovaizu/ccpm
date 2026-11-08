"""Decides how Claude Code's hook input reads and how the guard's answer goes back to it. No other
part of Lane knows that form.

Each hook entry that `lay.py write` lays runs this script with the plugin's name, as
`python3 -B "${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py" <plugin>`, and hands it the hook input on
standard input. It prints the answer as the hooks reference documents it, and exits 0. Where it
can't read the input, it exits 2 with why on standard error, which blocks the action on each event
that can block it.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "domain"))

import guard

# The events of a tool call, whose input names the tool and gives its input.
TOOL_EVENTS = ("PreToolUse", "PostToolUse")
# Who fixes a hook input out of its documented form.
CLAUDE_CODE = guard.CLAUDE_CODE


class _Unread(ValueError):
    """Hook input that this script can't read, with what's wrong."""


def plugin_root(script: str) -> str:
    """The plugin's folder, which holds the script at `<root>/hooks/lane/hook.py`.

    It reads the path that ran the script, and resolves no link in it, so that a link to Lane's
    code still gives the plugin that holds the link."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(script))))


def main(argv: list[str], text: str, environ: dict[str, str], root: str) -> tuple[str, int]:
    """What the hook prints, and its exit code.

    argv holds the command's words, with the plugin's name after the script. text holds the hook
    input, as Claude Code hands it on standard input. environ is the hook's environment, which
    gives the project's folder. root is the plugin's folder.
    """
    if len(argv) < 2:
        return _unread("lane", "the hook's command names no plugin", "the maker of the plugin"), 2
    name = argv[1]
    try:
        event = _event(text)
    except _Unread as why:
        return _unread(name, str(why), None), 2
    answer = guard.answer(name, root, environ.get("CLAUDE_PROJECT_DIR"), event)
    return _shown(event.name, answer), 0


def _unread(name: str, what: str, maker: str | None) -> str:
    who = (
        CLAUDE_CODE
        if maker is None
        else f"{maker} must lay its lanes again with Lane's lay.py write"
    )
    return (
        f"{name}: lane cannot check the lanes of this hook: {what}. Ask the main conversation for"
        f" the fix: {who}. Go on with the rest of your work meanwhile."
    )


def _event(text: str) -> guard.Event:
    """The event in the hook input.

    It raises _Unread where the input isn't a JSON object, or lacks a field that the hooks
    reference gives every such event.
    """
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    if not isinstance(data, dict):
        raise _Unread("the hook input is no JSON object")
    for key in ("hook_event_name", "session_id", "cwd"):
        if not isinstance(data.get(key), str):
            raise _Unread(f"the hook input gives no {key}")
    name = data["hook_event_name"]
    if name in TOOL_EVENTS:
        if not isinstance(data.get("tool_name"), str):
            raise _Unread(f"the hook input of {name} gives no tool_name")
        if not isinstance(data.get("tool_input"), dict):
            raise _Unread(f"the hook input of {name} gives no tool_input")
    return guard.Event(
        name=name,
        session=data["session_id"],
        cwd=data["cwd"],
        agent_id=data.get("agent_id"),
        agent_type=data.get("agent_type"),
        tool=data.get("tool_name"),
        tool_input=data.get("tool_input", {}),
        tool_response=data.get("tool_response"),
        prompt=data.get("prompt"),
        command=data.get("command_name"),
        stop_active=data.get("stop_hook_active") is True,
    )


def _shown(name: str, answer: guard.Answer) -> str:
    """The answer as the hook output of the event, or nothing where it says nothing."""
    out: dict[str, Any] = {}
    specific: dict[str, Any] = {}
    if answer.deny is not None or answer.ask is not None:
        decision = "deny" if answer.deny is not None else "ask"
        specific["permissionDecision"] = decision
        specific["permissionDecisionReason"] = answer.deny if decision == "deny" else answer.ask
    if answer.context is not None:
        specific["additionalContext"] = answer.context
    if specific:
        out["hookSpecificOutput"] = {"hookEventName": name, **specific}
    if answer.block is not None:
        out["decision"] = "block"
        out["reason"] = answer.block
    if answer.tell is not None:
        out["systemMessage"] = answer.tell
    return json.dumps(out) if out else ""


if __name__ == "__main__":
    shown, code = main(sys.argv, sys.stdin.read(), dict(os.environ), plugin_root(sys.argv[0]))
    if code:
        sys.stderr.write(shown)
    else:
        sys.stdout.write(shown)
    sys.exit(code)
