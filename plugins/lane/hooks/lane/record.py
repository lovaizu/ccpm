"""The layout of the run record, a file of each conversation in the system temp folder that only
grows, holding only what no later move gives again, so a run's folder found after the run is added
is a line of its own; and the run's state, which read_state reads once from a run's entries, so
that what each kind of entry means is written here alone."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable, TypedDict, Union, cast

from rules import Step


class Entry(TypedDict, total=False):
    """One line of the run record: its `kind`, one of `run`, `folder`, `start`, `turn_begun`,
    `turn`, `turn_ended`, `tie`, `drop`, `read`, `mark`, `result`, `back`, `stopped`, `typed`, and
    `ended`,
    the `run` it belongs to, the `agent_id` of the subagent whose move it is, None for the main
    conversation's, and the fields of that kind: a `folder` gives the run's plugin's folder, a
    `start` the `prompt` that the main conversation gave it, the prompt of the start it resumes for
    a resume, and the `steps` that the plugin's adapter of the rules gave for it, where it gave any,
    a `turn_begun` the `prompt` that began a turn of the main conversation after the run's first, a
    `turn` the main conversation's `role` at the turn's first call or end, the turn's `prompt`, and
    the `steps` that the plugin's adapter of the rules gave for it, each later entry of the main
    conversation until the next `turn` belonging to that turn, a `turn_ended` the turn's end that
    the guard let through, a `back` the `step` that a start or the main conversation went back to
    and the steps it `undone`, that step and each after it, whose earlier marks no longer count, a
    `stopped` the `agent_id` of a start that ended with no result, such as one stopped by TaskStop,
    and an `ended` the end of the run, once its order said the run ends."""

    kind: str
    run: str
    plugin_root: str
    skill: str
    words: str
    role: str
    tool_use_id: str
    agent_id: str | None
    path: str
    first_line: int
    last_line: int
    step: str
    item: str
    result: str
    command: str
    prompt: str
    steps: list[Step]
    undone: list[str]


@dataclass
class Run:
    """One run of a plugin's skill in a conversation, from the words typed after its command, with
    its plugin's folder, None until a `folder` entry gives it, and each entry of it in its order,
    among them each command, turn, start, read, mark, and result."""

    id: str
    session_id: str
    skill: str
    words: str
    plugin_root: str | None = None
    entries: list[Entry] = field(default_factory=list)

    @cached_property
    def state(self) -> RunState:
        """The run's state, read once from its entries; a run given more entries by
        dataclasses.replace reads its own."""
        return read_state(self.entries)


@dataclass
class Command:
    """A command of the run's plugin, typed by the person or called by the Skill tool, after the
    one that called the run, by its skill's name."""

    command: str


@dataclass
class Start:
    """A start of a subagent, by its `start` entry with its role, prompt, call, and any steps that
    the plugin's adapter of the rules gave: the subagent that its call's PostToolUse tied it to,
    None until then; whether its call failed, which drops it; whether it ended after its tie, by a
    result or a stop; and whether it was stopped with no result, such as by TaskStop."""

    entry: Entry
    tie: str | None = None
    dropped: bool = False
    ended: bool = False
    stopped: bool = False


@dataclass
class Result:
    """A result that a role gave by its reporter."""

    role: str
    result: str


@dataclass
class Done:
    """S12: what counts for a subagent, or for the main conversation's turn: the steps marked done,
    and each step's items marked done, the marks made before a `back` of the step it undid left
    out; each file's lines read; and the latest result, None for none."""

    steps: set[str] = field(default_factory=set)
    items: dict[str, set[str]] = field(default_factory=dict)
    lines: dict[str, set[int]] = field(default_factory=dict)
    result: str | None = None


@dataclass
class TurnAtHand:
    """S11: the main conversation's turn at hand, from the run's start or from the latest turn's
    end that the guard let through: whether such an end comes before it, the prompt that its
    `turn_begun` entry gives, None where it holds none, and its `turn` entry, with the role and the
    steps that hold the main conversation's moves in it, None until the turn's first call or
    end."""

    after_an_end: bool = False
    prompt: str | None = None
    entry: Entry | None = None


# A move of the run that its plugin's order sees.
OrderedMove = Union[Command, Start, Result]


@dataclass
class RunState:
    """What a run's entries mean, as read_state reads them: whether the run's order said it ends;
    each command, start, and result in their order; each `turn` entry, oldest first, and the turn
    at hand; the start that each subagent was last tied to; and what counts for each subagent, by
    its `agent_id`, and for the main conversation's turn, by None."""

    ended: bool = False
    moves: list[OrderedMove] = field(default_factory=list)
    turns: list[Entry] = field(default_factory=list)
    turn: TurnAtHand = field(default_factory=TurnAtHand)
    tied: dict[str, Start] = field(default_factory=dict)
    done: dict[str | None, Done] = field(default_factory=dict)
    # Each start by the tool_use_id of its call, which its tie and its drop name.
    calls: dict[str, Start] = field(default_factory=dict)

    @property
    def starts(self) -> list[Start]:
        """Each start of the run, in its order."""
        return [move for move in self.moves if isinstance(move, Start)]

    @property
    def commands(self) -> list[str]:
        """Each command after the one that called the run, in its order."""
        return [move.command for move in self.moves if isinstance(move, Command)]

    def done_by(self, agent_id: str | None) -> Done:
        """What counts for the subagent, or for the main conversation's turn by None."""
        return self.done.get(agent_id, Done())


def read_state(entries: list[Entry]) -> RunState:
    """The run's state.

    Takes: a run's entries, in the order the record holds them.
    Gives: the RunState they mean: a start tied by the `tie` of its call and dropped by its `drop`,
    and ended by a `result` or a `stopped` of the subagent it was last tied to; the turn at hand
    begun anew at each `turn_ended`, with its latest `turn_begun` and `turn`; what counts for the
    main conversation begun anew at each `turn`, as each turn's steps start afresh; and a `back`
    undoing the marks made before it of each step it names.
    Changes: nothing.
    Refuses: nothing.
    """
    state = RunState()
    for entry in entries:
        _READS[entry["kind"]](state, entry)
    return state


def _held_by_run(state: RunState, entry: Entry) -> None:
    """A `run` or a `folder` entry, which Run holds of itself."""


def _ended(state: RunState, entry: Entry) -> None:
    state.ended = True


def _typed(state: RunState, entry: Entry) -> None:
    state.moves.append(Command(entry["command"]))


def _start(state: RunState, entry: Entry) -> None:
    start = Start(entry)
    state.calls[entry["tool_use_id"]] = start
    state.moves.append(start)


def _tie(state: RunState, entry: Entry) -> None:
    start = state.calls[entry["tool_use_id"]]
    start.tie = _subagent(entry)
    state.tied[start.tie] = start


def _drop(state: RunState, entry: Entry) -> None:
    state.calls[entry["tool_use_id"]].dropped = True


def _stopped(state: RunState, entry: Entry) -> None:
    start = state.tied[_subagent(entry)]
    start.ended = start.stopped = True


def _result(state: RunState, entry: Entry) -> None:
    agent_id = entry.get("agent_id")
    state.moves.append(Result(entry["role"], entry["result"]))
    _done(state, agent_id).result = entry["result"]
    if agent_id is not None:
        state.tied[agent_id].ended = True


def _mark(state: RunState, entry: Entry) -> None:
    done = _done(state, entry.get("agent_id"))
    if "item" in entry:
        done.items.setdefault(entry["step"], set()).add(entry["item"])
    else:
        done.steps.add(entry["step"])


def _back(state: RunState, entry: Entry) -> None:
    done = _done(state, entry.get("agent_id"))
    for step in entry["undone"]:
        done.steps.discard(step)
        done.items.pop(step, None)


def _read(state: RunState, entry: Entry) -> None:
    lines = _done(state, entry.get("agent_id")).lines.setdefault(entry["path"], set())
    lines.update(range(entry["first_line"], entry["last_line"] + 1))


def _turn_begun(state: RunState, entry: Entry) -> None:
    state.turn.prompt = entry["prompt"]


def _turn(state: RunState, entry: Entry) -> None:
    state.turns.append(entry)
    state.turn.entry = entry
    state.done[None] = Done()


def _turn_ended(state: RunState, entry: Entry) -> None:
    state.turn = TurnAtHand(after_an_end=True)


def _done(state: RunState, agent_id: str | None) -> Done:
    """What counts for the subagent, or the main conversation by None, made where none counts
    yet."""
    return state.done.setdefault(agent_id, Done())


def _subagent(entry: Entry) -> str:
    """The `agent_id` of a tie or a stop, which a subagent's call or end always gives."""
    return cast(str, entry["agent_id"])


# What each kind of entry means for the run's state.
_READS: dict[str, Callable[[RunState, Entry], None]] = {
    "run": _held_by_run,
    "folder": _held_by_run,
    "ended": _ended,
    "typed": _typed,
    "start": _start,
    "tie": _tie,
    "drop": _drop,
    "stopped": _stopped,
    "result": _result,
    "mark": _mark,
    "back": _back,
    "read": _read,
    "turn_begun": _turn_begun,
    "turn": _turn,
    "turn_ended": _turn_ended,
}


def runs(session_id: str) -> list[Run]:
    """Where each run of the conversation stands.

    Takes: the conversation's `session_id`.
    Gives: each run that the record of the conversation holds, with its folder from its `folder`
    entry, and its entries in the order they were added; none where the conversation has no record
    yet.
    Changes: nothing.
    Refuses: OSError, where the record can't be read.
    """
    try:
        with open(_path(session_id), encoding="utf-8") as f:
            entries: list[Entry] = [json.loads(line) for line in f]
    except FileNotFoundError:
        return []
    found: dict[str, Run] = {}
    for entry in entries:
        if entry["kind"] == "run":
            found[entry["run"]] = Run(entry["run"], session_id, entry["skill"], entry["words"])
        run = found[entry["run"]]
        if entry["kind"] == "folder":
            run.plugin_root = entry["plugin_root"]
        run.entries.append(entry)
    return list(found.values())


def add(session_id: str, entries: list[Entry]) -> None:
    """Adds the entries to the record of the conversation, at its end, in one write.

    Takes: the conversation's `session_id`, and the entries, such as a new run with no folder at
    the skill's call, or a run's folder with each result that follows its routes.
    Gives: nothing.
    Changes: the record of the conversation in the system temp folder, made where it's missing.
    Refuses: OSError, where the record can't be written.
    """
    lines = "".join(json.dumps(entry) + "\n" for entry in entries)
    with open(_path(session_id), "a", encoding="utf-8") as f:
        f.write(lines)


def _path(session_id: str) -> str:
    """The record of the conversation, in the system temp folder."""
    return os.path.join(tempfile.gettempdir(), f"lane-{session_id}.jsonl")
