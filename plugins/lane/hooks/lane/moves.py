"""The moves of a flow, as lane's docs/flow.md says them: the move due, read from the flow its
plugin's hooks/lanes.json lays and from the orchestrator's calls the guard kept as each came back,
as called.py keeps them; the line telling it, which the guard tells the orchestrator as it starts,
as each call of a subagent of the flow comes back, and with the flow's sentence where it drifts; and
whether a call takes it. Nothing the orchestrator writes is read: a subagent's answer is what it
ended with, given back by the Agent call that started it in the foreground, or kept as it ended in
the background, as called.py keeps it."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, NamedTuple

from call import Call

# The tool the orchestrator starts each subagent of the flow with, and the field naming the
# subagent.
AGENT, TYPE = "Agent", "subagent_type"
# The status an Agent call comes back with once its subagent has ended, run in the foreground,
# and the one it comes back with as its subagent starts in the background, before it ends.
DONE, LAUNCHED = "completed", "async_launched"
# What an Agent call starting a subagent of the flow comes back as, as Claude Code hands it to a
# PostToolUse hook: what it gave back, of one of the two statuses, with the ID of the subagent it
# started, by which its end is found (hooks, Agent).
CAME_BACK = {
    "type": "object",
    "required": ["tool_response"],
    "properties": {
        "tool_response": {
            "type": "object",
            "required": ["status", "agentId"],
            "properties": {"status": {"enum": [DONE, LAUNCHED]}, "agentId": {"type": "string"}},
        }
    },
}
# The Markdown marks a line of an answer may be set in, left out at its two ends.
MARKS = "*_`"


class Run(NamedTuple):
    """The run of a flow: the flow, as hooks/lanes.json holds it, the plugin's name, and the
    orchestrator's calls kept, in the order they came back, each with its input, an object, and
    each start come back from the background with whether its subagent has ended and its answer,
    as called.flow_kept gives them; and whether the move due has reached the orchestrator since
    the last start of the flow came back, as `reached` reads it, true where not read."""

    flow: dict[str, Any]
    plugin: str
    kept: list[dict[str, Any]]
    told: bool = True


class Due(NamedTuple):
    """The move due: the position in the flow's order, from 0, of the subagent to start, None once
    the flow is done or while a subagent of it runs; what sent the run there, said, "" where the
    order alone did; and the subagent of the flow running in the background, as Claude Code names
    it, "" for none."""

    at: int | None
    why: str
    running: str = ""


def named(run: Run, at: int) -> str:
    """The subagent at the position in the flow's order, as Claude Code names a plugin's subagent,
    `<plugin>:<name>`."""
    return f"{run.plugin}:{run.flow['order'][at]}"


def due(run: Run) -> Due:
    """The move due, walking the calls kept: an Agent call starting the subagent due moves the run
    on once that subagent has ended, come back from the foreground or, from the background, ended
    since, to the position its back names where it is the `from` of a back and its answer answers
    the back's while, and else to the next, the flow done after the last; that call come back from
    the background, its subagent still running, leaves no move due while it runs; every other call,
    one come back of another status or with no subagent's ID among them, changes nothing."""
    order, at, why = run.flow["order"], 0, ""
    backs = {b["from"]: b for b in run.flow.get("back", [])}
    for kept in run.kept:
        if kept.get("tool") != AGENT or kept.get("failed"):
            continue
        if kept["input"].get(TYPE) != named(run, at):
            continue
        # A start come back not as CAME_BACK says is an error told as it came back, not a move.
        if kept.get("status") not in (DONE, LAUNCHED) or not kept.get("agent"):
            continue
        if kept["status"] == LAUNCHED and not kept.get("ended"):
            return Due(None, "", named(run, at))
        back = backs.get(at + 1)
        if back is not None and answers(str(kept.get("answer", "")), back["while"]):
            at, why = back["to"] - 1, f"{order[at]} answered `{back['while']}`."
        else:
            at, why = (at + 1 if order[at + 1 :] else None), ""
        if at is None:
            break
    return Due(at, why)


def starts(run: Run, tool: str, given: Mapping[str, Any]) -> bool:
    """Whether a call of the tool with the input starts a subagent the flow names: an Agent call
    naming it as Claude Code names a plugin's subagent."""
    names = [named(run, at) for at in range(len(run.flow["order"]))]
    return tool == AGENT and given.get(TYPE) in names


def last_start(run: Run) -> dict[str, Any] | None:
    """The last call kept that starts a subagent the flow names, as `starts` tells one; None where
    none is kept."""
    found = [k for k in run.kept if starts(run, str(k.get("tool")), k["input"])]
    return found[-1] if found else None


def reached(run: Run, said: list[str]) -> bool:
    """Whether the move due has reached the orchestrator, given what hooks told it since the last
    start of the flow came back, as its record holds them: where no start is kept, as it was told
    the first move as it started; where the last came back from the foreground, or failed, as it
    was told the move as that start came back; and else where one of them holds the line telling
    the move due, as the line told as the orchestrator starts again after a subagent ended in the
    background may not reach it."""
    last = last_start(run)
    if last is None or last.get("failed") or last.get("status") == DONE:
        return True
    return any(told(run) in s for s in said)


def told(run: Run) -> str:
    """The line telling the orchestrator the move due, by its position in the order, from 1, as
    an order may name a subagent more than once, after what sent the run there where anything did;
    to wait for the subagent of the flow running; or that the flow is done."""
    now = due(run)
    if now.running:
        return f"Wait for `{now.running}` to end: lane tells the next move once it has."
    if now.at is None:
        return "The flow is done: lane tells no more moves."
    move = f"The next move of the flow is move {now.at + 1}: start `{named(run, now.at)}`."
    return f"{now.why} {move}" if now.why else move


def taken(run: Run, call: Call) -> bool:
    """Whether the call takes the move due: an Agent call starting the subagent due, in the
    foreground or the background, once the move has reached the orchestrator, as the run's `told`
    says; none is due once the flow is done or while a subagent of it runs."""
    at = due(run).at
    starting = at is not None and call.tool == AGENT and call.given.get(TYPE) == named(run, at)
    return starting and run.told


def answers(answer: str, said: str) -> bool:
    """Whether the answer answers the text: a line of it is that text exactly, case as written, once
    the blanks around the line and the Markdown marks MARKS at its two ends are left out, so `more`
    on a line of its own answers `more` and `No more entries need the writer.` does not."""
    return any(line.strip().strip(MARKS) == said for line in answer.splitlines())
