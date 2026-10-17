"""Which of turn's agents a hook event comes from, what it was started with, and the run it belongs
to, read from what Claude Code keeps of each agent's conversation.

An agent's conversation is kept in `<transcript_path without .jsonl>/subagents/agent-<agent_id>.jsonl`,
its first record the prompt it was started with. That is Claude Code's own record, not a documented
hook input, so the hooks' tests hold its shape."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
)

import run

TURN = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def role(event: dict[str, Any]) -> str | None:
    """The name of turn's agent the event comes from, such as `up`, or None for any other."""
    kind = str(event.get("agent_type", ""))
    return kind.partition("turn:")[2] or None if event.get("agent_id") else None


def prompt(event: dict[str, Any]) -> str:
    """What the agent of the event was started with."""
    path = event.get("agent_transcript_path") or os.path.join(
        os.path.splitext(event["transcript_path"])[0],
        "subagents",
        f"agent-{event['agent_id']}.jsonl",
    )
    with open(path, encoding="utf-8") as f:
        return json.loads(f.readline())["message"]["content"]


def result(event: dict[str, Any]) -> str | None:
    """Where the result of the agent's run goes: the orchestrator's call says it, and each role's
    prompt says the run it is of."""
    try:
        given = json.loads(prompt(event))
    except (OSError, ValueError):
        return None
    key = "result" if role(event) == "up" else "run"
    value = given.get(key) if isinstance(given, dict) else None
    return os.path.join(event["cwd"], value) if isinstance(value, str) else None


def running(event: dict[str, Any]) -> dict[str, Any] | None:
    """The run the agent of the event belongs to, while it runs."""
    path = result(event)
    return run.running(path) if path else None
