"""The form of what a plugin's order takes and gives, as starts_due.in.schema.json and
starts_due.out.schema.json beside this module give it: the run as the order sees it, which facts
of the run record it holds among them, and the starts due or the run's end."""

from __future__ import annotations

from typing import TypedDict

from record import Run


class OrderMove(TypedDict, total=False):
    """A move of the run as the plugin's order sees it: its `kind`, one of `command`, `start`, and
    `result`, and the `command`, by its skill's name, such as `log:retry`, or the `role` started
    with the `prompt` that the main conversation gave it, or the `role` and the `result` it
    gave."""

    kind: str
    command: str
    role: str
    prompt: str
    result: str


class OrderRun(TypedDict):
    """The run as the plugin's order sees it: the skill that called it, the words typed after its
    command, and each of its moves in their order."""

    skill: str
    words: str
    moves: list[OrderMove]


class StartDue(TypedDict):
    """A role to start now, by its agent type, and how many times at once."""

    role: str
    count: int


class StartsDue(TypedDict, total=False):
    """What the plugin's order gives: the `starts` due now, none where the run waits, such as for
    the person's answer; or `ends`, true where the run ends."""

    starts: list[StartDue]
    ends: bool


def order_run(run: Run) -> OrderRun:
    """The run as the plugin's order sees it.

    Takes: the run as its record stands.
    Gives: its skill and words, and each command that called or moved it, each start made, and each
    result, in their order, each start with its prompt; a start whose Agent call failed, or that
    ended with no result, such as one stopped by TaskStop, is left out, so that the order gives its
    role due again.
    Changes: nothing.
    Refuses: nothing.
    """
    moves: list[OrderMove] = [{"kind": "command", "command": run.skill}]
    # Each start's move, by the tool_use_id of its call, and the call of each subagent's latest
    # start, so that a drop or a stop takes its start's move out.
    starts: dict[str, OrderMove] = {}
    latest: dict[str, str] = {}
    for entry in run.entries:
        kind = entry["kind"]
        if kind == "typed":
            moves.append({"kind": "command", "command": entry["command"]})
        elif kind == "start":
            start: OrderMove = {"kind": "start", "role": entry["role"], "prompt": entry["prompt"]}
            starts[entry["tool_use_id"]] = start
            moves.append(start)
        elif kind == "tie":
            latest[entry["agent_id"]] = entry["tool_use_id"]
        elif kind == "result":
            moves.append({"kind": "result", "role": entry["role"], "result": entry["result"]})
        elif kind in ("drop", "stopped"):
            use = entry["tool_use_id"] if kind == "drop" else latest[entry["agent_id"]]
            gone = starts[use]
            moves = [move for move in moves if move is not gone]
    return {"skill": run.skill, "words": run.words, "moves": moves}
