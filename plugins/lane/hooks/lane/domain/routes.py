"""Decides which moves the Routes make due: after the start of a Run, after each Result, and after
a command that the person types; whether a start, a resume, or an end of the main conversation's
turn is one of them; and where a run picked up from the Kept results stands."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from domain.laid_set import Move, Route
from domain.run_record import Result, Run


@dataclass(frozen=True)
class PickUp:
    """Where a Run picked up from the Kept results stands: `fresh` where they hold none or reach a
    Route that starts no more, so that the Run starts anew; else each Result in order, with the
    moves due after the last."""

    fresh: bool
    results: tuple[Result, ...] = ()
    moves: tuple[Move, ...] = ()


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


def opens_start(run: Run, role: str, text: str) -> bool:
    """Whether a start of the role with the text is one that the Run's moves open: a move due
    starts the role, the text is the one the Run keeps for it, and no Start of the role that runs
    took the same text."""
    raise NotImplementedError("routes.opens_start")


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
