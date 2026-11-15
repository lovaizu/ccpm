"""How each Run of a conversation stands, worked out from the run record's lines, the Routes, and
the Kept results alone: its Starts, its Results, its Approvals, the moves due, and whether it waits,
stands aside, or has ended."""

from __future__ import annotations

import dataclasses
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, Union

from adapters import KeptResult
from form import After, Move, Route, read_lanes
from manifest import plugin_name
from run_record import (
    Called,
    Ended,
    Gave,
    Line,
    Prompted,
    Shown,
    Started,
    SteppedAside,
    TextFailed,
    TextGiven,
    Tied,
    lines,
    record_path,
)

# Each line of a Run's record after its call.
Moving = Union[Prompted, Shown, Started, Tied, Gave, Ended, SteppedAside, TextFailed, TextGiven]


class OffRoutes(Exception):
    """Kept results that the Routes don't lead through, with the first that leaves them, so that the
    guard stops the command with why and who must fix it."""


@dataclass(frozen=True)
class Result:
    """A Result that a role or the skill gave in the Run."""

    role: str
    result: str


@dataclass(frozen=True)
class Start:
    """One start or resume of a role in the Run: its role, text, and run values, the call that made
    it, the agent_id it's tied to once tied, each Result it gave, whether it has ended, and whether
    it resumes a subagent that a Start before it started."""

    role: str
    text: str
    values: Mapping[str, str]
    tool_use_id: str
    agent_id: str | None
    results: tuple[str, ...]
    ended: bool
    resumed: bool = False


@dataclass(frozen=True)
class Approval:
    """The caller's own act on a Proposal that the Run showed: a person's reply after it, or the
    Run's call by an AI."""

    proposal_id: str
    by: Literal["person", "ai"]


@dataclass(frozen=True)
class Due:
    """A move due, with the text and run values of a start or resume."""

    move: Move
    text: str
    values: Mapping[str, str]


@dataclass(frozen=True)
class Left:
    """A start that the guard leaves out of the moves due, as the adapter gave that no work waits
    for it, with why in its place."""

    move: Move
    why: str


@dataclass(frozen=True)
class Run:
    """One run of one skill in the conversation, as it stands; `closing` where the skill's own
    Result ended it and no prompt has been typed since, so that the end of that turn is still held
    by the skill's Lanes; `awaiting` where the adapter of a start's text failed at the skill's call
    and hasn't answered since, so that the guard asks it again after each call of the main
    conversation."""

    id: str
    skill: str
    by: Literal["person", "ai"]
    words: str
    starts: tuple[Start, ...]
    results: tuple[Result, ...]
    shown: tuple[Shown, ...]
    approvals: tuple[Approval, ...]
    due: tuple[Move, ...]
    aside: bool
    ended: bool
    closing: bool = False
    awaiting: bool = False


@dataclass(frozen=True)
class Conversation:
    """Each Run of one conversation."""

    session_id: str
    runs: tuple[Run, ...]


def stand(
    session_id: str, lines: Sequence[Line], routes: Sequence[Route], plugin: str = ""
) -> Conversation:
    """Where each Run of the conversation stands.

    Takes: the conversation's session_id, the run record's lines, the plugin's Routes, and the
    plugin's name, by which a prompt `/<plugin>:<command>` is the plugin's command.
    Gives: each Run, its moves due those of the Route after its latest start, Result, typed
    command, or returned call, a Route after the plugin's command typed taking the place of those
    before, a start staying due beside each Start it made, as the guard gives it where the adapter
    gives a text other than theirs, a resume taken by its Start, and a start whose subagent ended
    with no Result due again; `awaiting` from the adapter's failure at the skill's call until it
    answers; a Run ended, and closing,
    by the skill's own Result where a move due starts no more by it, until a prompt is typed; a
    Run aside from the call of another plugin's skill, with the moves of the Route after that call
    due, until a Start.
    Changes: nothing.
    Refuses: nothing; a line of a Run that the Routes no longer name leaves that Run no moves due.
    Carries: the guard's working out of each Run on each event of S1 to S7, from `G->>RS: reads
    the lines`.
    """
    runs: dict[str, Run] = {}
    for line in lines:
        if isinstance(line, Called):
            runs[line.run] = _called(line, routes)
        else:
            runs[line.run] = _moved(runs[line.run], line, routes, plugin)
    return Conversation(session_id, tuple(runs.values()))


def _called(line: Called, routes: Sequence[Route]) -> Run:
    """A Run as its skill's call starts it, with the moves of the Route after its start due."""
    due = _moves(routes, line.skill, lambda after: after.kind == "first")
    return Run(line.run, line.skill, line.by, line.words, (), (), (), (), due, False, False)


def _moved(run: Run, line: Moving, routes: Sequence[Route], plugin: str) -> Run:
    """The Run after one more line of its record."""
    if isinstance(line, (Started, Tied, Ended)):
        return _of_start(run, line)
    if isinstance(line, Gave):
        return _gave(run, line, routes)
    if isinstance(line, Prompted):
        return _prompted(run, line, routes, plugin)
    if isinstance(line, SteppedAside):
        return _aside(run, line, routes)
    if isinstance(line, (TextFailed, TextGiven)):
        return dataclasses.replace(run, awaiting=isinstance(line, TextFailed))
    return dataclasses.replace(run, shown=(*run.shown, line))


def _of_start(run: Run, line: Started | Tied | Ended) -> Run:
    """The Run after a Start, which ends its standing aside and takes the resume it makes, while a
    start stays due beside it; its tie to an agent_id; or its subagent's end."""
    if isinstance(line, Started):
        start = Start(
            line.role, line.text, line.values, line.tool_use_id, None, (), False, line.resumed
        )
        due = list(run.due)
        if line.resumed and Move("resume", role=line.role) in due:
            due.remove(Move("resume", role=line.role))
        return dataclasses.replace(run, starts=(*run.starts, start), due=tuple(due), aside=False)
    if isinstance(line, Tied):
        starts = tuple(
            dataclasses.replace(s, agent_id=line.agent_id)
            if s.tool_use_id == line.tool_use_id
            else s
            for s in run.starts
        )
        return dataclasses.replace(run, starts=starts)
    return _ended(run, line)


def _ended(run: Run, line: Ended) -> Run:
    """The Run after a subagent's end: its Start ended, and due again where it gave no Result."""
    ended = [s for s in run.starts if s.agent_id == line.agent_id]
    starts = tuple(dataclasses.replace(s, ended=True) if s in ended else s for s in run.starts)
    again = [Move("start", role=s.role) for s in ended if not s.results]
    due = tuple(dict.fromkeys((*run.due, *again)))
    return dataclasses.replace(run, starts=starts, due=due)


def _prompted(run: Run, line: Prompted, routes: Sequence[Route], plugin: str) -> Run:
    """The Run after a prompt: the moves of a Route after the plugin's command typed, as
    `/<plugin>:<command>`, in place of those before, and a Run that its skill's Result ended no
    longer closing."""
    typed = line.text.split(maxsplit=1)[0] if line.text.strip() else ""
    due = _moves(
        routes,
        run.skill,
        lambda after: after.kind == "command" and typed == f"/{plugin}:{after.command}",
    )
    return dataclasses.replace(run, due=due or run.due, closing=False)


def _aside(run: Run, line: SteppedAside, routes: Sequence[Route]) -> Run:
    """The Run set aside by the call of another plugin's skill, with the moves of the Route after
    that call due."""
    due = _moves(
        routes, run.skill, lambda after: after.kind == "returned" and after.skill == line.skill
    )
    return dataclasses.replace(run, aside=True, due=due)


def _gave(run: Run, line: Gave, routes: Sequence[Route]) -> Run:
    """The Run after a Result: the skill's own ends it where a move due starts no more by it, and a
    role's makes the moves of the Route after it due."""
    results = (*run.results, Result(line.role, line.result))
    if line.agent_id is None and line.role == run.skill:
        ended = Move("no_more", result=line.result) in run.due
        return dataclasses.replace(run, results=results, due=(), ended=ended, closing=ended)
    starts = tuple(
        dataclasses.replace(s, results=(*s.results, line.result))
        if s.agent_id == line.agent_id
        else s
        for s in run.starts
    )
    due = _led(routes, run.skill, Result(line.role, line.result))
    return dataclasses.replace(run, starts=starts, results=results, due=due)


def _led(routes: Sequence[Route], skill: str, result: Result) -> tuple[Move, ...]:
    """The moves of each Route of the skill that goes after the Result."""
    return _moves(
        routes,
        skill,
        lambda after: (
            after.kind == "result" and (after.role, after.result) == (result.role, result.result)
        ),
    )


def _moves(routes: Sequence[Route], skill: str, after: Callable[[After], bool]) -> tuple[Move, ...]:
    """The moves of each Route of the skill that goes after what `after` takes."""
    return tuple(m for r in routes if r.skill == skill and after(r.after) for m in r.moves)


def where(root: str, session_id: str) -> Conversation:
    """Where each Run of the conversation stands, for a script that isn't a hook.

    Takes: the plugin's folder, whose hooks/lanes.json gives the Routes, and the session_id from
    the script's CLAUDE_CODE_SESSION_ID.
    Gives: the Conversation, as `stand` works it out from the conversation's run record.
    Changes: nothing.
    Refuses: run_record.Unreadable, and form.OutOfForm or FileNotFoundError for lanes.json, so
    that the script refuses with why.
    Carries: S2 `L->>G: asks where up's Run stands`, S6 `R->>G: asks where each Run stands`.
    """
    lanes = read_lanes(os.path.join(root, "hooks", "lanes.json"))
    name = plugin_name(root)
    return stand(session_id, lines(record_path(name, session_id)), lanes.proposal.routes, name)


def may_give(conversation: Conversation, role: str, routes: Sequence[Route]) -> tuple[str, ...]:
    """The Results that a role may give now in a Run of the conversation.

    Takes: the Conversation, the role or skill, and the Routes.
    Gives: each Result that a Route goes after for the role, or that a move due of the skill names
    to start no more by, in a Run that hasn't ended and, for a role, in which a Start of it runs;
    none where no Run allows it.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `alt a Result the role may give`.
    """
    given: list[str] = []
    for run in (r for r in conversation.runs if not r.ended):
        if role == run.skill:
            given += [m.result for m in run.due if m.kind == "no_more" and m.result]
        elif any(s.role == role and not s.ended for s in run.starts):
            given += [
                r.after.result
                for r in routes
                if r.skill == run.skill
                and r.after.kind == "result"
                and r.after.role == role
                and r.after.result
            ]
    return tuple(dict.fromkeys(given))


def pick_up(routes: Sequence[Route], skill: str, kept: Sequence[KeptResult]) -> tuple[Result, ...]:
    """The Results that a Run picked up in a new conversation takes from the Kept results.

    Takes: the Routes, the skill, and the Kept results in the order the run gave them.
    Gives: the Results, each one that a Route after the one before goes after; none where the Kept
    results are none or reach a Route that starts no more, as the run then starts anew.
    Changes: nothing.
    Refuses: OffRoutes, naming the first Kept result whose role no move due before it starts, or
    that no Route of the skill goes after.
    Carries: S7 `alt results that follow the Routes` and `results that don't follow them`.
    """
    due = _moves(routes, skill, lambda after: after.kind == "first")
    for each in kept:
        led = _led(routes, skill, Result(each.role, each.result))
        if Move("start", role=each.role) not in due or not led:
            raise OffRoutes(
                f"{each.role} gave `{each.result}` in the results kept, which no Route of {skill}"
                " leads to"
            )
        if any(m.kind == "no_more" for m in led):
            return ()
        due = led
    return tuple(Result(each.role, each.result) for each in kept)
