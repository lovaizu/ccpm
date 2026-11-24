"""How Claude Code is run for a piece: its command line, in its mode that asks no one, with only
the piece's tools allowed and the prompt on its standard input."""

from __future__ import annotations

from dataclasses import dataclass

from runner.carry import Piece


@dataclass(frozen=True)
class Output:
    """What one run of Claude Code gave: its exit code, its standard output, and its standard
    error."""

    code: int
    stdout: str
    stderr: str


def run(piece: Piece, conversation: str | None) -> Output:
    """Runs Claude Code once for the piece, in the piece's folder.

    Takes: the piece, and None for its first run, or the ID of its conversation to go on in.
    Gives: what Claude Code gave once it exited.
    Changes: what Claude Code does in the piece's folder.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.claude.run")
