"""What each of lane's hook entries runs: reads the event Claude Code hands on stdin, holds it to
the fields Claude Code documents, has the guard judge it where it is of a subagent of the plugin,
and answers in Claude Code's JSON output: a break denied with its sentence, an error denied and
told the user too, as a break is the subagent's to put right and an error the plugin's or Claude
Code's, which letting the call through would hide."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import IO, Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "core", "domain"))

import guard
import rules
import schema

# Who must fix a hook's command that does not name the plugin.
LAY_AGAIN = (
    "the plugin's maker must lay its lanes again with `lay.py write`, to write its hooks anew"
)


def event_in(held: str) -> dict[str, Any]:
    """The JSON Schema of the fields of the event of the name that lane reads, as the hooks
    reference documents them: the event's name, the folder it comes from, the tool and its input,
    and the type of the subagent that makes the call, where a subagent makes it."""
    fields = {
        "hook_event_name": {"const": held},
        "cwd": {"type": "string"},
        "tool_name": {"type": "string"},
        "tool_input": {"type": "object"},
    }
    return {
        "type": "object",
        "required": list(fields),
        "properties": {**fields, "agent_type": {"type": "string"}},
    }


def event_wrong(event: dict[str, Any], held: str) -> str:
    """Where the event is out of the fields of the event held, as the hooks reference documents
    them; "" where it is not."""
    out = schema.held(event_in(held), event)
    if out is not None:
        return out.told()
    if not os.path.isdir(event["cwd"]):
        return f"$.cwd: expected a folder, found {schema.shown(event['cwd'])}"
    return ""


def answer(said: list[guard.Said], plugin: str) -> dict[str, Any]:
    """What a PreToolUse hook answers Claude Code of what was said, each headed by the plugin's
    name: the call denied with each line said as the reason, which Claude Code shows the subagent,
    and each error as the systemMessage too, which Claude Code shows the user; nothing where
    nothing was said, which lets the call go on."""
    if not said:
        return {}
    told = "\n".join(f"{plugin}: {s.text}" for s in said)
    user = "\n".join(f"{plugin}: {s.text}" for s in said if s.error)
    denied = {"hookEventName": "PreToolUse", "permissionDecision": "deny"}
    found: dict[str, Any] = {"systemMessage": user} if user else {}
    return {**found, "hookSpecificOutput": {**denied, "permissionDecisionReason": told}}


def main(held: str, argv: list[str], stdin: IO[str], stdout: IO[str], root: str) -> None:
    """Answers on stdout the event of the hook's event held, read from stdin, for the plugin at
    root, the folder Claude Code gives as CLAUDE_PLUGIN_ROOT, whose name the hook's command gives
    as its one word. A command not in that form stops each subagent's call, and an event that is
    no JSON object every call, as no subagent can be told from them; the main conversation's calls
    go on, as lane checks subagents alone."""
    plugin = " ".join(argv)
    text = stdin.read()
    try:
        event = json.loads(text)
    except ValueError:
        event = None
    if not re.fullmatch(rules.NAME, plugin):
        if not isinstance(event, dict) or "agent_type" in event:
            wrong = (
                f"its command gives `{plugin}`, not the plugin's name, as `lay.py write` writes it"
            )
            write(
                stdout, answer([guard.cannot("the lanes of this hook", wrong, LAY_AGAIN)], "lane")
            )
        return
    if not isinstance(event, dict):
        said = guard.cannot(
            "the lanes of this hook", "it was handed no JSON object", guard.CLAUDE_CODE
        )
        write(stdout, answer([said], plugin))
        return
    agent = event.get("agent_type")
    if not isinstance(agent, str) or not agent.startswith(f"{plugin}:"):
        return
    said = guard.check(root, plugin, agent[len(plugin) + 1 :], event, event_wrong(event, held))
    write(stdout, answer(said, plugin))


def write(stdout: IO[str], found: dict[str, Any]) -> None:
    """Writes the answer on stdout as the one JSON object Claude Code reads there, nothing where it
    is empty."""
    if found:
        stdout.write(json.dumps(found) + "\n")
