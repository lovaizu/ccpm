"""runner.py's command line: what a runner takes as it starts, both as it's started and as the
runner reads it."""

from __future__ import annotations

from runner.carry import Piece

# The exit code, standard output, and standard error of a command.
Answer = tuple[int, str, str]


def line(piece: Piece) -> tuple[list[str], str]:
    """The command line that starts a runner of the piece.

    Takes: the piece.
    Gives: the arguments that run `runner.py` by this Python, and the text for its standard input,
    which holds the prompt.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.command.line")


def main(argv: list[str], stdin: str) -> Answer:
    """The exit code, stdout, and stderr of `runner.py` with the arguments and standard input.

    Takes: the arguments and standard input that `line` gives.
    Gives: 0 once the piece is carried to its end, as `carry.carry` says.
    Changes: what `carry.carry` changes.
    Refuses: 2 with what's wrong where the arguments or standard input aren't what `line` gives.
    """
    raise NotImplementedError("runner.command.main")
