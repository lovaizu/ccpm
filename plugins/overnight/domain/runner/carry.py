"""How a piece is carried to its end: run, then resumed in its conversation after each reset of
the usage limit, waiting a set while where a stop gives no reset."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Piece:
    """One piece of work as its runner carries it: the repository whose record it keeps, its
    number, the folder it works in, its prompt, and the tools it may use."""

    repository: str
    number: int
    folder: str
    prompt: str
    tools: tuple[str, ...]


def carry(piece: Piece) -> None:
    """Carries the piece until its conversation ends.

    Takes: the piece, whose record hand-over wrote as running.
    Gives: nothing, once the piece's record says done or failed.
    Changes: through `pieces.record`, records each wait from the stop to the reset, the piece
    running again after it, and its end: done with its last words, or failed with its error.
    Refuses: nothing: each end of the conversation is recorded, however often the limit stops it.
    """
    raise NotImplementedError("runner.carry.carry")
