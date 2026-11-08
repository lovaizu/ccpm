"""lane's entries in a plugin's hooks/hooks.json: one for the plugin in each event lane acts on,
those of a tool call run on every call, as Claude Code reads no hooks from a plugin agent's own
file, and hook.py acting by the event's agent_type; every other entry of the plugin left as it was,
and the file read and written.

Each entry's command first checks that Python can run lane's code. Where it cannot, PreToolUse's
reads the event with the shell alone, and denies a call of a subagent with lanes, telling the
subagent and the user what to install; it lets any other call through, as lane checks those
subagents alone. Every other event's goes on, telling nothing, as each call of the subagent is
stopped meanwhile."""

from __future__ import annotations

import json
import os
import shlex
from typing import Any

import rules
from proposal import Stop

EVENT = "PreToolUse"
# Each event lane acts on, the first a tool call's that is stopped where lane cannot check it.
EVENTS = [
    EVENT,
    "PostToolUse",
    "SubagentStart",
    "SubagentStop",
    "UserPromptExpansion",
    "UserPromptSubmit",
    "Stop",
]
# The events of a tool call or a subagent, whose entries match each one; the others, of the main
# conversation's prompt and turn, take no matcher.
MATCHED_EVENTS = EVENTS[:4]
# What lane's entries run, by which lay.py tells them from the plugin's own, of this shape and of
# the old, one for each subagent and event.
CODE = "/hooks/lane/"
# Python writes no compiled files into the plugin's folder, which would show as the plugin's own
# changes where it lies in the user's repository, as Q12 of
# plugins/rn/domain/best-practices/plugin/best-practice.md keeps what is used only while it runs out
# of the repository.
SCRIPT = 'exec python3 -B "${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/{script}.py" '
INSTALL = "{plugin}: install Python 3.9 or later, run as python3, for its hooks to run"
PYTHON = 'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'
# The event read by the shell alone, as Claude Code writes it, with a blank after a colon or none.
CHECK = (
    PYTHON + ' || {{ e=; while IFS= read -r l || [ -n "$l" ]; do e="$e$l"; l=; done;'
    ' case "$e" in {patterns}) echo {answer};; esac; exit 0; }}'
)
MATCHED = """*'"agent_type":"{agent}"'*|*'"agent_type": "{agent}"'*"""


def command(plugin: str, names: list[str], event: str) -> str:
    """The command of the event's entry for the plugin whose subagents of the names have lanes laid
    or are named by its routes."""
    run = SCRIPT.format(script=event.lower()) + plugin
    if event != EVENT:
        return f"{PYTHON} || exit 0; {run}"
    said = INSTALL.format(plugin=plugin)
    denied = {
        "hookEventName": EVENT,
        "permissionDecision": "deny",
        "permissionDecisionReason": said,
    }
    answer = shlex.quote(json.dumps({"systemMessage": said, "hookSpecificOutput": denied}))
    patterns = "|".join(MATCHED.format(agent=f"{plugin}:{n}") for n in names)
    return CHECK.format(patterns=patterns, answer=answer) + "; " + run


def entry(plugin: str, names: list[str], event: str) -> dict[str, Any]:
    """lane's entry of the event for the plugin whose subagents of the names have lanes laid or are
    named by its routes: run on every tool call or subagent, within the seconds rules.TIMEOUT
    gives; at PreToolUse the call blocked where the hook fails, so a call lane could not check is
    stopped rather than let through."""
    run = {"type": "command", "timeout": rules.TIMEOUT, "command": command(plugin, names, event)}
    blocked = {"onFailure": "block"} if event == EVENT else {}
    matched = {"matcher": "*"} if event in MATCHED_EVENTS else {}
    return {**matched, "hooks": [{**run, **blocked}]}


def ours(given: dict[str, Any]) -> bool:
    """Whether an entry of hooks.json is lane's, of this shape or the old: a hook of it runs lane's
    code."""
    return any(CODE in str(h.get("command", "")) for h in given.get("hooks", []))


def put(hooks: dict[str, Any], plugin: str, names: list[str]) -> dict[str, Any]:
    """The hooks with lane's entries taken out of every event, and lane's entry for the subagents of
    the names put in each event lane acts on, in the place of the first taken out there, after every
    other entry otherwise, an event lane's entries were not in after every other event; none where
    no subagent has lanes or routes. An event left with no entry is left out, where lane's were all
    it held."""
    events: dict[str, Any] = {}
    for event, given in hooks.get("hooks", {}).items():
        kept = [e for e in given if not ours(e)]
        if event in EVENTS and names:
            at = next((n for n, e in enumerate(given) if ours(e)), len(given))
            kept.insert(at, entry(plugin, names, event))
        if kept or not given:
            events[event] = kept
    for event in EVENTS if names else []:
        events.setdefault(event, [entry(plugin, names, event)])
    return {**hooks, "hooks": events}


def read(root: str) -> dict[str, Any]:
    """The hooks.json of the plugin at root, an empty one where there is none; stops where it is not
    in Claude Code's shape, an object whose hooks hold, for each event, a list of entries whose
    hooks are a list of objects."""
    path = os.path.join(root, "hooks", "hooks.json")
    if not os.path.exists(path):
        return {"hooks": {}}
    hooks: Any = None
    try:
        with open(path, encoding="utf-8") as f:
            hooks = json.load(f)
    except ValueError:
        pass
    events = hooks.get("hooks") if isinstance(hooks, dict) else None
    lists = list(events.values()) if isinstance(events, dict) else [None]
    if not all(isinstance(e, list) and all(map(shaped, e)) for e in lists):
        raise Stop(f"lay.py: {path} is not in the shape Claude Code reads; fix it and run again.")
    return hooks


def shaped(given: Any) -> bool:
    """Whether an entry of hooks.json is an object whose hooks are a list of objects."""
    each = given.get("hooks", []) if isinstance(given, dict) else None
    return isinstance(each, list) and all(isinstance(h, dict) for h in each)


def written(root: str, hooks: dict[str, Any]) -> None:
    """Writes the hooks into the plugin's hooks/hooks.json, indented by two, as Claude Code reads
    them."""
    os.makedirs(os.path.join(root, "hooks"), exist_ok=True)
    with open(os.path.join(root, "hooks", "hooks.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(hooks, indent=2, ensure_ascii=False) + "\n")
