"""The order in which a piece is set up apart from the person's work and started."""

from __future__ import annotations

from pieces.record import Handed


def hand_over(repository: str, prompt: str, tools: tuple[str, ...]) -> Handed:
    """Hands the piece over: its number, its worktree, its runner started, and its record.

    Takes: the repository's root, the piece's prompt, and each tool it may use.
    Gives: the piece handed over.
    Changes: makes the piece's worktree, starts its runner apart from the session, and records
    the piece as running, with that process as its runner.
    Refuses: `worktree.Refused` where git can't make the worktree, and OSError where the runner
    can't be started.
    """
    raise NotImplementedError("handover.hand.hand_over")
