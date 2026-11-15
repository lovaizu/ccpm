"""The words of each answer the guard gives: the moves due with each start's text, a Result and the
moves after it, a stop with a Lane's sentence and what the role may do, and why the guard can't
check with who must fix it, each opened by the plugin's name."""

from __future__ import annotations

from collections.abc import Sequence

from form import Move
from lanes.kind import Broken, CantCheck
from runs import Due, Left


def due(plugin: str, moves: Sequence[Due | Left]) -> str:
    """The moves due, such as ``changelog: Start `changelog:writer` with `Carry out your steps`.``,
    with why in place of each start left out, such as ``No work waits for `changelog:writer`:
    <why>.``, and each call of another plugin's skill, such as ``Call `lint:check` by the Skill
    tool.``; nothing where no move is one of these or the move to start no more.

    Carries: S5 `G-->>M: the moves due, each start with its text`, with why in place of each start
    that `G->>G: leaves that start out of the moves due`, S7 `G-->>M: the start due`.
    """
    said = _moves(plugin, moves)
    return f"{plugin}: {said}" if said else ""


def gave(plugin: str, role: str, result: str, moves: Sequence[Due | Left]) -> str:
    """A Result and the moves of its Route, such as ``changelog: writer gave `written`. Start ...``,
    with why in place of each start left out, as `due` says it.

    Carries: S5 `G-->>M: the Result, and the moves of its Route`, with why in place of each start
    that `G->>G: leaves that start out of the moves due`, and `start no more subagents`.
    """
    return f"{plugin}: {role} gave `{result}`. {_moves(plugin, moves)}".rstrip()


def ended_unheld(plugin: str, role: str, moves: Sequence[Due | Left]) -> str:
    """That a subagent ended with no Result, and its start due again, or why in its place where the
    start is left out, as `due` says it.

    Gives: such as ``changelog: writer ended with no Result.`` and, on the next line, the moves due
    as `due` gives them.

    Carries: S5 `G-->>M: that it ended with no Result, and its start due again`.
    """
    return "\n".join(
        x for x in (f"{plugin}: {role} ended with no Result.", due(plugin, moves)) if x
    )


def text_failed(plugin: str, moves: Sequence[Move], why: str) -> str:
    """Each start due whose text the adapter failed to give at the skill's call, with why, such as
    ``changelog: Start `changelog:writer` with the text its adapter gives once it can; now
    <why>.``, as the skill's own steps may make what the adapter reads.

    Carries: S5 `G->>G: gives that start with why, and lets the call run`.
    """
    said = [
        f"Start `{plugin}:{m.role}` with the text its adapter gives once it can; now {why}."
        for m in moves
        if m.kind == "start"
    ]
    return f"{plugin}: {' '.join(said)}"


def stopped(plugin: str, broken: Broken) -> str:
    """A stop: the Lane's sentence, and what the role may do.

    Carries: S2 `G-->>UP: stops it`, S5 `G-->>M: stops it`, S6 `G-->>SA: stops it`.
    """
    return "\n".join(x for x in (f"{plugin}: {broken.sentence}", broken.may) if x)


def _moves(plugin: str, moves: Sequence[Due | Left]) -> str:
    """The words of the moves due: each start with its text, the move to start no more, and why in
    place of each start left out."""
    said = [_move(plugin, d) for d in moves]
    return " ".join(dict.fromkeys(x for x in said if x))


def _move(plugin: str, told: Due | Left) -> str:
    """The words of one move due, or of why in place of a start left out; none for a move that
    the main conversation is told nothing of."""
    move = told.move
    if isinstance(told, Left):
        return f"No work waits for `{plugin}:{move.role}`: {told.why}."
    if move.kind == "start":
        return f"Start `{plugin}:{move.role}` with `{told.text}`."
    if move.kind == "call":
        return f"Call `{move.skill}` by the Skill tool."
    return "Start no more subagents." if move.kind == "no_more" else ""


def cant_check(plugin: str, cant: CantCheck) -> str:
    """Why the guard can't check, and who must fix it.

    Carries: S5 `G-->>M: why and who must fix it`, S6 `G-->>SA: stops it, with why and who must fix
    it`, S7 `G-->>U: stops the command, with why and who must fix it`.
    """
    return f"{plugin}: Lane can't check this: {cant.why}. {cant.who}."
