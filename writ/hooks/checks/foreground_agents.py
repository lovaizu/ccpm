"""Run writ's own agents in the foreground, so whoever called writ gets a finished work back."""

from typing import Optional

WRIT_AGENTS = ("writ:generator", "writ:first-user")


def is_writ_agent_start(input_data: dict) -> bool:
    tool_input = input_data.get("tool_input") or {}
    return input_data.get("tool_name") == "Agent" and tool_input.get("subagent_type") in WRIT_AGENTS


def update(input_data: dict) -> Optional[dict]:
    """Return the tool input to use instead, or None to leave it as it is."""
    if not is_writ_agent_start(input_data):
        return None
    tool_input = dict(input_data.get("tool_input") or {})
    if tool_input.get("run_in_background") is False:
        return None
    tool_input["run_in_background"] = False
    return tool_input
