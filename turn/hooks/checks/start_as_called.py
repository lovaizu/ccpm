"""The orchestrator starts its run with the call it was given, so the run is the one the calling AI
asked for."""

import json
from typing import Any

import agents


def check(event: dict[str, Any]) -> list[str]:
    command = str(event["tool_input"].get("command", ""))
    if agents.role(event) != "up" or event["tool_name"] != "Bash" or "turn.py start" not in command:
        return []
    given = command[command.find("{") : command.rfind("}") + 1]
    try:
        same = json.loads(given) == json.loads(agents.prompt(event))
    except ValueError:
        same = False
    if same:
        return []
    return ["start the run with the call as it was given, your prompt, unchanged"]
