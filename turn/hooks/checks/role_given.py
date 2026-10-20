"""Each role is started in its turn with the prompt the script printed last, or, once it is started,
sent the message the script printed to the agent it names, so it is given what it is to be given
and nothing an AI copied wrong or added. A role replies only by ending with its form, which turn's hook keeps for the
orchestrator, so a message of its own to the orchestrator would only stop the orchestrator's
reading. Any agent of the run may tell `main`, the calling AI's conversation, what it will do or
what is done, as no step waits on it. The orchestrator's own record is kept as it starts its first role, for the
learner, which learns from every agent of the run."""

from __future__ import annotations

import json
from typing import Any

import agents
import run

ROLES = (run.GENERATOR, run.FIRST_USER, run.EVALUATOR, run.LEARNER)
# Where SendMessage reaches the conversation the calling AI runs in.
CALLER = "main"


def check(event: dict[str, Any]) -> list[str]:
    tool = event["tool_input"]
    if event["tool_name"] == "SendMessage":
        return messaged(event, tool)
    agent = tool.get("subagent_type")
    if event["tool_name"] != "Agent" or agent not in ROLES:
        return []
    given = prompt(tool)
    kept = run.running(given["run"]) if given else None
    if given is None or kept is None:
        return [f"start {agent} with what turn.py printed last as its prompt, as it is"]
    if "check" in kept:
        return ["give your check with `turn.py next` first; no role starts before it"]
    step = kept["next"]
    if "to" in step:
        said = (
            f"send {step['agent']} what turn.py printed last with SendMessage, to {step['to']}, as"
            " it is; it is started already"
        )
        return [said]
    if step["agent"] == agent and json.loads(step["prompt"]) == given:
        if event.get("agent_id") and "orchestrator" not in kept:
            kept["orchestrator"] = agents.transcript(event)
            run.write(given["run"], {"running": kept})
        return []
    return [f"start {step['agent']} with what turn.py printed last as its prompt, as it is"]


def messaged(event: dict[str, Any], tool: dict[str, Any]) -> list[str]:
    """A message to the calling AI goes; the orchestrator's goes as the script printed it; a role's
    reply goes only as its form."""
    if tool.get("to") == CALLER:
        return []
    if agents.role(event) == "up":
        return sent(event, tool)
    if f"turn:{agents.role(event)}" in ROLES:
        return [
            "reply with your form alone, as your last message; turn's hook keeps it for the orchestrator"
        ]
    return []


def sent(event: dict[str, Any], tool: dict[str, Any]) -> list[str]:
    """The orchestrator sends only the message due, not answered yet, to the agent it goes to."""
    kept = agents.running(event)
    if kept is None:
        return []
    step = kept.get("next", {})
    due = "to" in step and "reply" not in step
    if (
        due
        and tool.get("to") == step["to"]
        and parsed(tool.get("message")) == json.loads(step["message"])
    ):
        return []
    return ["send only what turn.py printed last, with its `to` and `message` as they are"]


def parsed(text: Any) -> Any:
    try:
        return json.loads(str(text))
    except ValueError:
        return None


def prompt(tool: dict[str, Any]) -> dict[str, Any] | None:
    """The role's prompt, when it is JSON naming a run."""
    try:
        given = json.loads(tool.get("prompt", ""))
    except ValueError:
        return None
    return given if isinstance(given, dict) and isinstance(given.get("run"), str) else None
