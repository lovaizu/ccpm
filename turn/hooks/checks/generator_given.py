"""The generator is started with the prompt the script printed last, so it is given the CCS, the
work and what was sent back, and nothing an AI copied wrong or added."""

import json
from typing import Any

import run


def check(event: dict[str, Any]) -> list[str]:
    tool = event["tool_input"]
    if event["tool_name"] != "Agent" or tool.get("subagent_type") != "turn:generator":
        return []
    try:
        given = json.loads(tool.get("prompt", ""))
        kept = run.running(given["run"])
        if kept is not None and json.loads(kept["prompt"]) == given:
            return []
    except (ValueError, KeyError, TypeError):
        pass
    return ["start turn:generator with what turn.py printed last as its prompt, as it is"]
