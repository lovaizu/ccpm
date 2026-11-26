"""How rn's cases make the files that rn reads, each in the form that its use reads it: a best
practice as its best-practice.json holds it, and the input that Claude Code gives rn's hook before a
tool call.

Each helper writes or gives what the documents name, and nothing of how rn's code reads it, so
that a case calls rn's parts only through their interfaces."""

from __future__ import annotations

import functools
import json
import os
from typing import Any

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
RN = os.path.join(TOP, "plugins", "rn")
PRACTICES = os.path.join(RN, "domain", "best-practices")


@functools.cache
def _practice(kind: str) -> str:
    with open(os.path.join(PRACTICES, kind, "best-practice.json"), encoding="utf-8") as f:
        return f.read()


def practice(kind: str) -> dict[str, Any]:
    """rn's best practice of the kind, read from the JSON of its best-practice.json."""
    return json.loads(_practice(kind))


def judged_by(kind: str) -> dict[str, Any]:
    """What an evaluator judges by, of rn's best practice of the kind, as practice.judged's
    contract names it: the goal's `what` and its factors, each condition with its id, about, and
    what alone."""
    goal = practice(kind)["goal"]
    return {
        "what": goal["what"],
        "critical_success_factors": [
            {
                "id": factor["id"],
                "what": factor["what"],
                "necessary_conditions": [
                    {"id": each["id"], "about": each["about"], "what": each["what"]}
                    for each in factor["necessary_conditions"]
                ],
            }
            for factor in goal["critical_success_factors"]
        ],
    }


def write_json(path: str, value: Any) -> None:
    """Writes the value as JSON at the path, its folder made."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=1)
        f.write("\n")


# The hook's input.


def hook_input(cwd: str, tool: str, tool_input: Any, agent: Any = None) -> str:
    """The JSON that Claude Code gives a PreToolUse hook on stdin for a call of the tool with its
    input, made in the folder, by the agent, as `agent_type` names it, or by the main
    conversation, which names none, where the agent is None."""
    called: dict[str, Any] = {
        "session_id": "abc123",
        "cwd": cwd,
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": tool_input,
        "tool_use_id": "toolu_01",
    }
    if agent is not None:
        called.update({"agent_id": "a1", "agent_type": agent})
    return json.dumps(called)
