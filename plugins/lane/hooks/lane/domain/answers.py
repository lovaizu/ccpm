"""The words of each answer the guard gives: the moves due with each start's text, a Result and the
moves after it, a stop with a Lane's sentence and what the role may do, and why the guard can't
check with who must fix it, each opened by the plugin's name."""

from __future__ import annotations

from collections.abc import Sequence

from lanes.kind import Broken, CantCheck
from runs import Due


def due(plugin: str, moves: Sequence[Due]) -> str:
    """The moves due, such as ``changelog: Start `changelog:writer` with `Carry out your steps`.``,
    or nothing where no move due is a start or the move to start no more.

    Carries: S5 `G-->>M: the moves due, each start with its text`, S7 `G-->>M: the start due`.
    """
    said = _moves(plugin, moves)
    return f"{plugin}: {said}" if said else ""


def gave(plugin: str, role: str, result: str, moves: Sequence[Due]) -> str:
    """A Result and the moves of its Route, such as ``changelog: writer gave `written`. Start ...``.

    Carries: S5 `G-->>M: the Result, and the moves of its Route`, and `start no more subagents`.
    """
    return f"{plugin}: {role} gave `{result}`. {_moves(plugin, moves)}".rstrip()


def ended_unheld(plugin: str, role: str, moves: Sequence[Due]) -> str:
    """That a subagent ended with no Result, and its start due again.

    Carries: S5 `G-->>M: that it ended with no Result, and its start due again`.
    """
    raise NotImplementedError("answers.ended_unheld")


def stopped(plugin: str, broken: Broken) -> str:
    """A stop: the Lane's sentence, and what the role may do.

    Carries: S2 `G-->>UP: stops it`, S5 `G-->>M: stops it`, S6 `G-->>SA: stops it`.
    """
    return "\n".join(x for x in (f"{plugin}: {broken.sentence}", broken.may) if x)


def _moves(plugin: str, moves: Sequence[Due]) -> str:
    """The words of the moves due: each start with its text, and the move to start no more."""
    said = [
        f"Start `{plugin}:{d.move.role}` with `{d.text}`."
        if d.move.kind == "start"
        else "Start no more subagents."
        for d in moves
        if d.move.kind in ("start", "no_more")
    ]
    return " ".join(dict.fromkeys(said))


def cant_check(plugin: str, cant: CantCheck) -> str:
    """Why the guard can't check, and who must fix it.

    Carries: S5 `G-->>M: why and who must fix it`, S6 `G-->>SA: stops it, with why and who must fix
    it`, S7 `G-->>U: stops the command, with why and who must fix it`.
    """
    raise NotImplementedError("answers.cant_check")
