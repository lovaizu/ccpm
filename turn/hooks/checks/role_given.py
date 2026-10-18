"""Each role is started in its turn with the prompt the script printed last, so it is given what it
is to be given and nothing an AI copied wrong or added, and the evaluator starts only once the
orchestrator's findings are kept. The orchestrator's own record is kept as it starts its first role,
for the learner, which learns from every agent of the run."""

from __future__ import annotations

import json
from typing import Any

import agents
import run

ROLES = (run.GENERATOR, run.FIRST_USER, run.EVALUATOR, run.LEARNER)


def check(event: dict[str, Any]) -> list[str]:
    tool = event["tool_input"]
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
    if step["agent"] == agent and json.loads(step["prompt"]) == given:
        if event.get("agent_id") and "orchestrator" not in kept:
            kept["orchestrator"] = agents.transcript(event)
            run.write(given["run"], {"running": kept})
        return []
    return [f"start {step['agent']} with what turn.py printed last as its prompt, as it is"]


def prompt(tool: dict[str, Any]) -> dict[str, Any] | None:
    """The role's prompt, when it is JSON naming a run."""
    try:
        given = json.loads(tool.get("prompt", ""))
    except ValueError:
        return None
    return given if isinstance(given, dict) and isinstance(given.get("run"), str) else None
