"""Decides where each Run of a conversation stands, worked out from the lines of its run record, for
the guard, `result.py`, and `lay.py` alike, and which moves the Routes of its skill make due: after
the start of a Run, after each Result, after a command that the person types, and after another
plugin's run that a move called; whether a start, a resume, a call of another plugin's skill, or an
end of the main conversation's turn is one of them; and where a run picked up from the Kept results
stands."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace

from domain.fault import Fault
from domain.laid_set import CALL, NO_MORE, RESUME, START, WAIT, LaidSet, Move, Route, routes_of
from domain.run_record import (
    CALLED,
    ENDED,
    LAID,
    PROMPTED,
    SHOWN,
    TURN_ENDED,
    TYPED,
    Called,
    Line,
    Noted,
    Result,
    Run,
    Start,
    Tied,
)


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
    that a Route of its goes after, none after the moves start no more; `aside` the other plugin's
    skill from a Noted CALLED line until a later Start or resume of the Run, which makes a move of
    the Route after that call; and the Run ended once its skill gave its own Result, `ending` until
    a Noted TURN_ENDED line, or once a later call of its skill begins a new Run of it, as each call
    line does. Raises Fault as `first` does."""
    runs: list[Run] = []
    for line in lines:
        if isinstance(line, Called):
            runs.append(_begun(line, laid_set, session, runs))
        elif isinstance(line, Start):
            _started(line, runs)
        elif isinstance(line, Tied):
            _tied(line, runs)
        elif isinstance(line, Result):
            _gave(line, laid_set, runs)
        elif line.what in (TYPED, CALLED):
            _moved(line, laid_set, runs)
        elif line.what == ENDED:
            _ended(line, runs)
        else:
            _noted(line, runs)
    return tuple(runs)


def _begun(line: Called, laid_set: LaidSet, session: str, runs: list[Run]) -> Run:
    for run in runs:
        if run.skill == line.skill:
            run.ended = True
    moves = [] if laid_set.proposes else list(first(routes_of(laid_set, line.skill)))
    return Run(laid_set.plugin, line.skill, session, line.by, moves=moves)


def _going_run(runs: Sequence[Run], skill: str) -> Run | None:
    return next((run for run in reversed(runs) if run.skill == skill and not run.ended), None)


def _started(line: Start, runs: list[Run]) -> None:
    run = _going_run(runs, line.skill)
    if run is None:
        return
    resumed = next((s for s in run.starts if line.resumes and s.number == line.resumes), None)
    if resumed is not None:
        line = replace(line, agent=resumed.agent, running=True)
    run.starts.append(line)
    run.aside = ""
    kind = RESUME if line.resumes else START
    opened = next((m for m in run.moves if m.kind == kind and m.role == line.role), None)
    if opened is not None:
        run.moves.remove(opened)


def _tied(line: Tied, runs: list[Run]) -> None:
    for run in runs:
        for place, start in enumerate(run.starts):
            if start.number == line.start:
                run.starts[place] = replace(start, agent=line.agent, running=True)


def _of_agent(runs: Sequence[Run], agent: str) -> tuple[Run, int] | None:
    """The Run and the place of the last Start that ties the subagent, None where none does."""
    for run in reversed(runs):
        for place in reversed(range(len(run.starts))):
            if run.starts[place].agent == agent:
                return run, place
    return None


def _gave(line: Result, laid_set: LaidSet, runs: list[Run]) -> None:
    if not line.agent:
        _skill_gave(line, runs)
        return
    found = _of_agent(runs, line.agent)
    if found is None:
        return
    run, place = found
    result = replace(line, start=run.starts[place].number)
    run.results.append(result)
    moves = after_result(routes_of(laid_set, run.skill), result)
    if not no_more(run.moves):
        run.moves.extend(moves)


def _skill_gave(line: Result, runs: list[Run]) -> None:
    """The skill's own Result, which ends the Run of the skill it names."""
    run = _going_run(runs, line.role)
    if run is not None:
        run.results.append(line)
        run.ended = run.ending = True


def _moved(line: Noted, laid_set: LaidSet, runs: list[Run]) -> None:
    """The moves of each Run that goes on after a command that the person typed, or of the one Run
    whose move due called the other plugin's skill, which then stands aside."""
    for run in runs:
        routes = routes_of(laid_set, run.skill)
        if run.ended:
            continue
        if line.what == TYPED:
            after = after_command(routes, line.text)
            waited = [
                replace(m, waits_for="") if m.waits_for == line.text else m for m in run.moves
            ]
            run.moves = list(after) if after is not None else waited
        elif opens_call(run, line.text):
            run.moves.remove(Move(CALL, line.text))
            run.moves.extend(_moves_after(routes, line.text))
            run.aside = line.text
            return


def _ended(line: Noted, runs: list[Run]) -> None:
    """A subagent's end that reached the main conversation: its Start runs no more, and, where it
    gave no Result since, as one that TaskStop stopped, its start or resume is due again."""
    found = _of_agent(runs, line.agent)
    if found is None:
        return
    run, place = found
    ended = run.starts[place] = replace(run.starts[place], running=False)
    if not run.ended and not any(r.start == ended.number for r in run.results):
        run.moves.append(Move(RESUME if ended.resumes else START, ended.role))


def _noted(line: Noted, runs: list[Run]) -> None:
    if line.what == TURN_ENDED:
        for each in runs:
            each.ending = False
        return
    run = next((each for each in reversed(runs) if not each.ended), None)
    if run is None:
        return
    if line.what == SHOWN:
        run.shown, run.prompted = line.text, False
    elif line.what == PROMPTED:
        run.prompted = True
    elif line.what == LAID:
        run.ended = True


def first(routes: Sequence[Route]) -> tuple[Move, ...]:
    """The moves of the Route `first`. Raises Fault, with the plugin's maker to fix it by running
    `/lane:up` again, where no Route is `first`."""
    return _moves_after(routes, "first")


def _moves_after(routes: Sequence[Route], after: str) -> tuple[Move, ...]:
    for route in routes:
        if route.after == after:
            return route.moves
    raise Fault(
        f"no Route goes after `{after}`, so run `/lane:up` again to lay the Routes anew",
        "the plugin's maker",
    )


def after_result(routes: Sequence[Route], result: Result) -> tuple[Move, ...]:
    """The moves of the Route after the role's result. Raises Fault as `first` does where no Route
    goes after it."""
    return _moves_after(routes, f"{result.role} {result.result}")


def after_command(routes: Sequence[Route], command: str) -> tuple[Move, ...] | None:
    """The moves of the Route that goes after the command that the person typed, such as
    `/changelog:pause`, or None where no Route goes after it."""
    return next((route.moves for route in routes if route.after == command), None)


def goes_after(run: Run, routes: Sequence[Route], command: str) -> bool:
    """Whether a Route of the Run's skill goes after the command that the person typed, such as
    `/changelog:pause`, or a move of the Run waits for it."""
    waits = any(move.waits_for == command for move in run.moves)
    return waits or after_command(routes, command) is not None


def due(moves: Sequence[Move], typed: str) -> tuple[Move, ...]:
    """The moves that are due now: each that waits for no command, and each that waits for the
    command `typed`, "" where the person typed none."""
    return tuple(move for move in moves if move.waits_for in ("", typed))


def opens_start(run: Run, role: str, text: str, given: str) -> bool:
    """Whether a start of the role with the text is one that the Run's moves open: a move due
    starts the role, the text is `given`, the text that the adapter gives for the role now or else
    Lane's, and no Start of the role that runs took the same text."""
    opened = any(m.kind == START and m.role == role for m in due(run.moves, ""))
    taken = any(s.role == role and s.running and s.text == text for s in run.starts)
    return opened and text == given and not taken


def opens_call(run: Run, skill: str) -> bool:
    """Whether a call of the skill, `<plugin>:<skill>`, is one that the Run's moves open: a move due
    calls that skill of another plugin."""
    return Move(CALL, skill) in due(run.moves, "")


def opens_resume(run: Run, agent: str) -> bool:
    """Whether a resume of the subagent is one that the Run's moves open: a move due resumes its
    role, and the Run started the subagent, which runs no more."""
    start = next((s for s in reversed(run.starts) if s.agent == agent), None)
    if start is None or start.running:
        return False
    return Move(RESUME, start.role) in due(run.moves, "")


def may_end_turn(run: Run) -> bool:
    """Whether the main conversation may end its turn in the Run: a move due is a wait or waits for
    a command, a subagent of the Run runs, no move is due, or the moves start no more, where the
    Lanes of the skill hold the end until it gives its result."""
    if not run.moves or no_more(run.moves) or any(s.running for s in run.starts):
        return True
    return any(m.kind == WAIT or m.waits_for for m in run.moves)


def holds(run: Run, role: str) -> bool:
    """Whether the Run goes on and takes a result of the role now: of a subagent of a Start of the
    Run that runs, or of its skill once a move due starts no more, as only that move ends a Run."""
    if run.ended:
        return False
    if run.skill == role:
        return any(move.kind == NO_MORE for move in due(run.moves, ""))
    return any(start.role == role and start.running for start in run.starts)


def no_more(moves: Sequence[Move]) -> bool:
    """Whether the moves are the one move that starts no more."""
    return len(moves) == 1 and moves[0].kind == NO_MORE


def pick_up(routes: Sequence[Route], kept: Sequence[Result]) -> PickUp:
    """Where a Run stands that picks up from the Kept results, in the order the run gave them.
    Raises Fault, naming the first Result that no Route goes after, with the plugin's maker to fix
    the adapter or the records, where they don't follow the Routes."""
    raise NotImplementedError("routes.pick_up")
