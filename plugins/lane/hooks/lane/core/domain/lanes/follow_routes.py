"""follow_routes: the orchestrator starts the subagent it is told to start, by the routes, and makes
no other call while that start is due; while a subagent it started runs in the background, it
starts no other, but more runs of that one where the routes fan it out, its other calls and its end
going on; it resumes no run that ended with no result, as a run started again stands in its place;
once no start is left, it is free. Laid from
the routes, with the result command on the last step of each subagent that gives a result."""

from __future__ import annotations

from typing import Any

from routes import Next

ACTION = "follow"
WORDING = "Start each subagent you are told to start, until you are told to start no more."
# What the last step of a subagent giving a result says, with the commands it gives them by.
RESULT = "End by running `<commands>`."
# The tool the orchestrator starts a subagent with, and the one it resumes a run with.
AGENT = "Agent"
MESSAGE = "SendMessage"


def started(tool: str, given: dict[str, Any], named: list[str], plugin: str) -> str | None:
    """The subagent of the names, of the plugin, that the call starts, by the type it gives as
    Claude Code names a plugin's subagent, `<plugin>:<name>`; None where the call starts none of
    them."""
    # No tool Claude Code names sorts before Agent.
    starting = tool == AGENT  # pragma: no mutate
    kind = given.get("subagent_type") if starting else None
    found = [n for n in named if kind == f"{plugin}:{n}"]
    if not found:
        return None
    # The names are each named once, so one at most is started.
    return found[0]  # pragma: no mutate


def allows(tool: str, given: dict[str, Any], due: Next, plugin: str) -> bool:
    """Whether the orchestrator's call goes through, the next start being `due`:
    while a start is due, only that start; while a subagent runs in the background, any call but a
    start, or but a start of another where more runs of it may start; once no start is left,
    any."""
    if due.kind == "start":
        return started(tool, given, [due.name], plugin) is not None
    # Here a next start is `end` or `wait`, `end` the first of them in order.
    if due.kind == "end":  # pragma: no mutate
        return True
    if due.more and started(tool, given, [due.name], plugin) is not None:
        return True
    # No tool Claude Code names sorts before Agent.
    return tool != AGENT  # pragma: no mutate


def resumes(tool: str, given: dict[str, Any], runs: list[str]) -> bool:
    """Whether the call resumes one of the runs, by their IDs, with a message sent to it."""
    return tool == MESSAGE and given.get("to") in runs


def ends(due: Next) -> bool:
    """Whether the orchestrator may end, the next start being `due`: only while no start is due."""
    return due.kind != "start"
