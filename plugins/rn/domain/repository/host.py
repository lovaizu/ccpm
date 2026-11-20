"""Decides how rn's code reaches git and gh, the only programs outside rn that it runs, so that a
test puts a double of them in their place."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Callable, NamedTuple


class Ran(NamedTuple):
    """What a program that rn ran gave: its exit code, its stdout, and its stderr."""

    code: int
    out: str
    err: str


# A program run as rn's code runs git or gh: the command's words, from `git` or `gh` on, and the
# folder it runs in, to what it gave. `run` is the real one; a test passes a double.
Host = Callable[[Sequence[str], str], Ran]


def run(argv: Sequence[str], cwd: str) -> Ran:
    """Runs git or gh as a process of its own.

    Takes: the command's words, whose first is `git` or `gh`, and the folder to run it in.
    Gives: its exit code, stdout, and stderr, whatever the code, as the caller judges the result.
    Changes: whatever the command changes.
    Refuses: Wrong where the first word is neither `git` nor `gh`; CantRun where the program isn't
    found or can't start, naming it.
    """
    raise NotImplementedError("repository.host.run")
