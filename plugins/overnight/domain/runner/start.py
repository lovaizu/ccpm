"""How a runner is started as a process of its own, apart from the session, by each OS's own
means."""

from __future__ import annotations

from runner.carry import Piece


def start(piece: Piece) -> int:
    """Starts a runner of the piece, detached from the session and its terminal.

    Takes: the piece, whose worktree exists.
    Gives: the ID of the runner's process, which goes on once the session closes.
    Changes: starts the process, by the command line that `command.line` gives.
    Refuses: OSError, with the system's words, where the process can't be started.
    """
    raise NotImplementedError("runner.start.start")
