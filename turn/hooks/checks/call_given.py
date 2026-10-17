"""A call to turn's orchestrator is checked before it is made, so a call turn cannot take is
mended by the calling AI where it was written, before any run starts."""

from typing import Any

import call


def check(event: dict[str, Any]) -> list[str]:
    tool = event["tool_input"]
    if event["tool_name"] != "Agent" or tool.get("subagent_type") != "turn:up":
        return []
    try:
        call.check(call.parse(str(tool.get("prompt", ""))))
    except call.Stop as stop:
        return [f"{stop}; start turn:up with the call alone as its prompt"]
    return []
