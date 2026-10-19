"""Which of turn's agents a hook event comes from, what it was started with, and the run it belongs
to, read from what Claude Code keeps of each agent's conversation.

An agent's conversation is kept in `<transcript_path without .jsonl>/subagents/agent-<agent_id>.jsonl`,
its first record the prompt it was started with. That is Claude Code's own record, not a documented
hook input, so the hooks' tests hold its shape. turn's scripts, which the hooks import, are found
by the folder hooks.json puts on PYTHONPATH."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import run

TURN = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Where the result goes, by the key of the agent's prompt that names it: the orchestrator's call
# names it as the result, and each role's prompt as the run it is of.
NAMED = {"up": "result"}

# turn's script as the orchestrator and each role run it, its path quoted or not, and the step it
# runs.
SCRIPT = re.compile(r"""turn\.py["']?\s+(start|next|given|parts|record)\b""")


def runs(command: str, step: str) -> bool:
    """Whether the command runs turn's script for the step, `start`, `next`, `given`, `parts` or
    `record`."""
    return any(m.group(1) == step for m in SCRIPT.finditer(command))


def role(event: dict[str, Any]) -> str | None:
    """The name of turn's agent the event comes from, such as `up`, or None for any other."""
    kind = str(event.get("agent_type", ""))
    return kind.partition("turn:")[2] or None if event.get("agent_id") else None


def reply(event: dict[str, Any]) -> str | None:
    """The reply the agent of the event ends with: the message it hands back with SubagentHandback,
    or, where Claude Code ends an agent on plain text, its last message at SubagentStop; None for
    any other event, and at SubagentStop after a handback, which gives no last message."""
    name = event["hook_event_name"]
    if (name, event.get("tool_name")) == ("PreToolUse", "SubagentHandback"):
        return str(event["tool_input"].get("message", ""))
    last = event.get("last_assistant_message", "") if name == "SubagentStop" else None
    return None if last is None else str(last)


def transcript(event: dict[str, Any]) -> str:
    """Where Claude Code keeps the conversation of the agent of the event."""
    return event.get("agent_transcript_path") or os.path.join(
        os.path.splitext(event["transcript_path"])[0],
        "subagents",
        f"agent-{event['agent_id']}.jsonl",
    )


def prompt(event: dict[str, Any]) -> str:
    """What the agent of the event was started with."""
    with open(transcript(event), encoding="utf-8") as f:
        return json.loads(f.readline())["message"]["content"]


def result(event: dict[str, Any]) -> str | None:
    """Where the result of the agent's run goes: the orchestrator's call says it, and each role's
    prompt says the run it is of."""
    try:
        given = json.loads(prompt(event))
    except (OSError, ValueError):
        return None
    value = given.get(NAMED.get(str(role(event)), "run")) if isinstance(given, dict) else None
    return os.path.join(event["cwd"], value) if isinstance(value, str) else None


def running(event: dict[str, Any]) -> dict[str, Any] | None:
    """The run the agent of the event belongs to, while it runs."""
    path = result(event)
    return run.running(path) if path else None
