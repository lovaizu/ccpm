"""The moves of a flow, as lane's docs/flow.md says them: the move due, read from the flow its
plugin's hooks/lanes.json lays and from the orchestrator's calls the guard kept as each came back,
as called.py keeps them; the line telling it, which the guard tells the orchestrator as it starts,
as each call of a subagent of the flow comes back, and with the flow's sentence where it drifts; and
whether a call takes it. Nothing the orchestrator writes is read: a subagent's answer is what the
Agent call that started it gave back, kept with the call."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, NamedTuple

from call import Call

# The tool the orchestrator starts each subagent of the flow with, the field naming the subagent,
# and the field that starts it in the background, where its call comes back before it ends.
AGENT, TYPE, BACKGROUND = "Agent", "subagent_type", "run_in_background"
# The status an Agent call comes back with once its subagent has ended, run in the foreground,
# and the one it comes back with as its subagent starts in the background, with no answer.
DONE, LAUNCHED = "completed", "async_launched"
# What an Agent call starting a subagent of the flow comes back as, as Claude Code hands it to a
# PostToolUse hook: what it gave back, of one of the two statuses (hooks, Agent).
CAME_BACK = {
    "type": "object",
    "required": ["tool_response"],
    "properties": {
        "tool_response": {
            "type": "object",
            "required": ["status"],
            "properties": {"status": {"enum": [DONE, LAUNCHED]}},
        }
    },
}
# Who must fix it where a start of the flow came back from the background, where lane cannot read
# its answer: Claude Code moves a subagent there on the user's Ctrl+B, or on its own after it has
# run about two minutes where automatic backgrounding is on, and does neither with this variable
# set (env-vars, CLAUDE_CODE_DISABLE_BACKGROUND_TASKS), which is the user's to set, not the
# plugin's.
FOREGROUND = (
    "whoever runs the plugin must set the environment variable"
    " `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` to `1`, with which Claude Code moves no subagent to"
    " the background, and run it again"
)
# The Markdown marks a line of an answer may be set in, left out at its two ends.
MARKS = "*_`"


class Run(NamedTuple):
    """The run of a flow: the flow, as hooks/lanes.json holds it, the plugin's name, and the
    orchestrator's calls kept, in the order they came back, each with its input, an object, as
    called.py keeps it."""

    flow: dict[str, Any]
    plugin: str
    kept: list[dict[str, Any]]


class Due(NamedTuple):
    """The move due: the position in the flow's order, from 0, of the subagent to start, None once
    the flow is done or lane cannot read it; what sent the run there, said, "" where the order
    alone did; and the start that came back from the background, as kept, whose answer lane
    cannot read, None for none."""

    at: int | None
    why: str
    lost: dict[str, Any] | None = None


def named(run: Run, at: int) -> str:
    """The subagent at the position in the flow's order, as Claude Code names a plugin's subagent,
    `<plugin>:<name>`."""
    return f"{run.plugin}:{run.flow['order'][at]}"


def due(run: Run) -> Due:
    """The move due, walking the calls kept: an Agent call starting the subagent due, come back
    from the foreground, moves the run on, to the position its back names where it is the `from` of
    a back and its answer answers the back's while, and else to the next, the flow done after the
    last; that call come back from the background, with no answer, leaves no move lane can read;
    every other call, that one of another status among them, changes nothing."""
    order, at, why = run.flow["order"], 0, ""
    backs = {b["from"]: b for b in run.flow.get("back", [])}
    for kept in run.kept:
        if kept.get("tool") != AGENT or kept.get("failed"):
            continue
        if kept["input"].get(TYPE) != named(run, at):
            continue
        if kept.get("status") == LAUNCHED:
            return Due(None, "", kept)
        if kept.get("status") != DONE:
            continue
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


def unread(lost: dict[str, Any]) -> str:
    """What is wrong where the move due is lost, given the start that came back from the
    background, as `due` gives it: lane cannot read its answer."""
    started = f"`{lost['input'][TYPE]}`"
    return f"{started} came back from the background, where lane cannot read its answer"


def told(run: Run) -> str:
    """The line telling the orchestrator the move due, by its position in the order, from 1, as
    an order may name a subagent more than once, after what sent the run there where anything did;
    or that the flow is done."""
    now = due(run)
    if now.at is None:
        return "The flow is done: lane tells no more moves."
    start = f"start `{named(run, now.at)}` in the foreground."
    move = f"The next move of the flow is move {now.at + 1}: {start}"
    return f"{now.why} {move}" if now.why else move


def taken(run: Run, call: Call) -> bool:
    """Whether the call takes the move due: an Agent call starting the subagent due, not in the
    background; none is due once the flow is done."""
    at = due(run).at
    return (
        at is not None
        and call.tool == AGENT
        and call.given.get(TYPE) == named(run, at)
        and not call.given.get(BACKGROUND)
    )


def answers(answer: str, said: str) -> bool:
    """Whether the answer answers the text: a line of it is that text exactly, case as written, once
    the blanks around the line and the Markdown marks MARKS at its two ends are left out, so `more`
    on a line of its own answers `more` and `No more entries need the writer.` does not."""
    return any(line.strip().strip(MARKS) == said for line in answer.splitlines())
