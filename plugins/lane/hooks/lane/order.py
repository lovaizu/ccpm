"""The form of what a plugin's order takes and gives, as starts_due.in.schema.json and
starts_due.out.schema.json beside this module give it: the run as the order sees it, which facts
of the run record it holds among them, and the starts due or the run's end."""

from __future__ import annotations

from typing import TypedDict

from record import Command, Result, Run


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
    command, the session ID of the conversation it runs in, and each of its moves in their
    order."""

    skill: str
    words: str
    session: str
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
    Gives: its skill and words, the conversation's session ID, and each command that called or
    moved it, each start made, and each result, in their order, each start with its prompt; a
    start whose Agent call failed, or that ended with no result, such as one stopped by TaskStop,
    is left out, so that the order gives its role due again.
    Changes: nothing.
    Refuses: nothing.
    """
    moves: list[OrderMove] = [{"kind": "command", "command": run.skill}]
    for move in run.state.moves:
        if isinstance(move, Command):
            moves.append({"kind": "command", "command": move.command})
        elif isinstance(move, Result):
            moves.append({"kind": "result", "role": move.role, "result": move.result})
        elif not (move.dropped or move.stopped):
            moves.append(
                {"kind": "start", "role": move.entry["role"], "prompt": move.entry["prompt"]}
            )
    return {"skill": run.skill, "words": run.words, "session": run.session_id, "moves": moves}
