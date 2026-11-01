"""The moves of a flow, as lane's docs/flow.md says them: the move due, read from the flow its
plugin's hooks/lanes.json lays and from the orchestrator's calls the guard kept as each came back,
as called.py keeps them; the line telling it, which the guard tells the orchestrator as it starts,
as each call of a subagent of the flow comes back, and with the flow's sentence where it drifts; and
whether a call takes it. Nothing the orchestrator writes is read: a subagent's answer is what the
Agent call that started it gave back, kept with the call."""

from __future__ import annotations

from typing import Any, NamedTuple

from call import Call

# The tool the orchestrator starts each subagent of the flow with, the field naming the subagent,
# and the field that starts it in the background, where its call comes back before it ends.
AGENT, TYPE, BACKGROUND = "Agent", "subagent_type", "run_in_background"
# The status an Agent call comes back with once its subagent has ended, run in the foreground.
DONE = "completed"
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
    alone did; and the ID of the start that came back from the background, whose answer lane
    cannot read, "" for none."""

    at: int | None
    why: str
    lost: str = ""


def named(run: Run, at: int) -> str:
    """The subagent at the position in the flow's order, as Claude Code names a plugin's subagent,
    `<plugin>:<name>`."""
    return f"{run.plugin}:{run.flow['order'][at]}"


def due(run: Run) -> Due:
    """The move due, walking the calls kept: an Agent call starting the subagent due, come back
    from the foreground, moves the run on, to the position its back names where it is the `from` of
    a back and its answer answers the back's while, and else to the next, the flow done after the
    last; that call come back from the background, with no answer, leaves no move lane can read,
    the flow held no more; every other call changes nothing."""
    order, at, why = run.flow["order"], 0, ""
    backs = {b["from"]: b for b in run.flow.get("back", [])}
    for kept in run.kept:
        if kept.get("tool") != AGENT or kept.get("failed"):
            continue
        if kept["input"].get(TYPE) != named(run, at):
            continue
        if kept.get("status") != DONE:
            return Due(None, "", str(kept.get("id", "")))
        back = backs.get(at + 1)
        if back is not None and answers(str(kept.get("answer", "")), back["while"]):
            at, why = back["to"] - 1, f"{order[at]} answered `{back['while']}`."
        else:
            at, why = (at + 1 if order[at + 1 :] else None), ""
        if at is None:
            break
    return Due(at, why)


def told(run: Run) -> str:
    """The line telling the orchestrator the move due, after what sent the run there where
    anything did; or that the flow is done."""
    now = due(run)
    if now.at is None:
        return "The flow is done: lane tells no more moves."
    move = f"The next move of the flow is to start `{named(run, now.at)}` in the foreground."
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
