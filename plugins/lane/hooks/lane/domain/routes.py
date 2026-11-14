"""Decides where each Run of a conversation stands, worked out from the lines of its run record, for
the guard, `result.py`, and `lay.py` alike, and which moves the Routes of its skill make due: after
the start of a Run, after each Result, after a command that the person types, and after another
plugin's run that a move called; whether a start, a resume, a call of another plugin's skill, or an
end of the main conversation's turn is one of them; and where a run picked up from the Kept results
stands."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from domain.laid_set import LaidSet, Move, Route
from domain.run_record import Line, Result, Run


@dataclass(frozen=True)
class PickUp:
    """Where a Run picked up from the Kept results stands: `fresh` where they hold none or reach a
    Route that starts no more, so that the Run starts anew; else each Result in order, with the
    moves due after the last."""

    fresh: bool
    results: tuple[Result, ...] = ()
    moves: tuple[Move, ...] = ()


def stand(lines: Sequence[Line], laid_set: LaidSet, session: str) -> tuple[Run, ...]:
    """Each Run of the conversation, in the order their skills were called, as the lines of its run
    record give it: each Start of the Run by the skill it keeps, tied to the subagent that a Tied
    line names and running until a Noted line of that subagent's end; each Result of a subagent for
    the Start its tie names and of the main conversation for the skill it names, as its role; the
    moves open by the Routes of the Run's skill after its call, each Result, and each command typed
    that a Route of its goes after; `aside` the other plugin's skill from a Noted CALLED line until
    a later Start or resume of the Run, which makes a move of the Route after that call; and the Run
    ended once a Route's one move starts no more, or
    once a later call of its skill begins a new Run of it, as each call line does. Raises Fault as
    `first` does."""
    raise NotImplementedError("routes.stand")


def first(routes: Sequence[Route]) -> tuple[Move, ...]:
    """The moves of the Route `first`. Raises Fault, with the plugin's maker to fix it by running
    `/lane:up` again, where no Route is `first`."""
    raise NotImplementedError("routes.first")


def after_result(routes: Sequence[Route], result: Result) -> tuple[Move, ...]:
    """The moves of the Route after the role's result. Raises Fault as `first` does where no Route
    goes after it."""
    raise NotImplementedError("routes.after_result")


def after_command(routes: Sequence[Route], command: str) -> tuple[Move, ...] | None:
    """The moves of the Route that goes after the command that the person typed, such as
    `/changelog:pause`, or None where no Route goes after it."""
    raise NotImplementedError("routes.after_command")


def due(moves: Sequence[Move], typed: str) -> tuple[Move, ...]:
    """The moves that are due now: each that waits for no command, and each that waits for the
    command `typed`, "" where the person typed none."""
    raise NotImplementedError("routes.due")


def opens_start(run: Run, role: str, text: str, given: str) -> bool:
    """Whether a start of the role with the text is one that the Run's moves open: a move due
    starts the role, the text is `given`, the text that the adapter gives for the role now or else
    Lane's, and no Start of the role that runs took the same text."""
    raise NotImplementedError("routes.opens_start")


def opens_call(run: Run, skill: str) -> bool:
    """Whether a call of the skill, `<plugin>:<skill>`, is one that the Run's moves open: a move due
    calls that skill of another plugin."""
    raise NotImplementedError("routes.opens_call")


def opens_resume(run: Run, agent: str) -> bool:
    """Whether a resume of the subagent is one that the Run's moves open: a move due resumes its
    role, and the Run started the subagent, which runs no more."""
    raise NotImplementedError("routes.opens_resume")


def may_end_turn(run: Run) -> bool:
    """Whether the main conversation may end its turn in the Run: a move due is a wait or waits for
    a command, a subagent of the Run runs, or no move is due."""
    raise NotImplementedError("routes.may_end_turn")


def no_more(moves: Sequence[Move]) -> bool:
    """Whether the moves are the one move that starts no more."""
    raise NotImplementedError("routes.no_more")


def pick_up(routes: Sequence[Route], kept: Sequence[Result]) -> PickUp:
    """Where a Run stands that picks up from the Kept results, in the order the run gave them.
    Raises Fault, naming the first Result that no Route goes after, with the plugin's maker to fix
    the adapter or the records, where they don't follow the Routes."""
    raise NotImplementedError("routes.pick_up")
