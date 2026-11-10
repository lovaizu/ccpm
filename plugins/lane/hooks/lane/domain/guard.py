"""The guard's decision: which call of a role goes on, and what each stop says."""

from __future__ import annotations

from typing import Any

from domain.lanes import TYPES

CLAUDE_CODE = "Run Claude Code 2.1.319 or later."


def decide(event: Any, laid: Any, plugin: str) -> str | None:
    """None where the call goes on, or the text that a stop gives the role.

    `event` is the PreToolUse event as Claude Code handed it. `laid` is the rules that lay.py write
    laid in hooks/lanes.json, already held to that form, or a text that says why the hook couldn't
    read them. The guard checks only a role of `plugin` with a rule laid. A call that the guard
    can't check stops, and the stop says who must fix it."""
    if not isinstance(event, dict):
        return (
            f"{plugin}: Lane can't check this call, as Claude Code handed it no JSON object."
            f" {CLAUDE_CODE}"
        )
    agent = event.get("agent_type")
    if not isinstance(agent, str) or not agent.startswith(f"{plugin}:"):
        return None
    name = agent[len(plugin) + 1 :]
    if isinstance(laid, str):
        return (
            f"{plugin}: Lane can't check the call of {name}, as {laid}. The maker of {plugin} must"
            " lay its proposal again with lay.py write."
        )
    role = laid["subagents"].get(name)
    if role is None or event.get("tool_name") != "Bash":
        return None
    run_only = [
        lane["takes"]
        for step in role["steps"]
        for lane in step["lanes"]
        if lane["lane"] == "run_only"
    ]
    if not run_only:
        return None
    given = event.get("tool_input")
    command = given.get("command") if isinstance(given, dict) else None
    if not isinstance(command, str):
        return (
            f"{plugin}: Lane can't check the call of {name}, as its command isn't text."
            f" {CLAUDE_CODE}"
        )
    commands = [each for takes in run_only for each in takes]
    if TYPES["run_only"].allows(command, commands):
        return None
    named = ", ".join(f"`{each}`" for each in commands)
    return (
        f"{plugin}: {TYPES['run_only'].sentence(run_only[0])}\n"
        f"The commands you may run, each word for word: {named}."
    )
