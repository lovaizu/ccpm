"""Decides how rn's code reaches git and gh, the only programs outside rn that it runs, so that a
test puts a double of them in their place."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from typing import Callable, NamedTuple

from fault import CantRun, Wrong


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
    if argv[0] not in ("git", "gh"):
        raise Wrong(f"rn runs only git and gh, not {argv[0]!r}")
    try:
        done = subprocess.run(list(argv), cwd=cwd, capture_output=True, text=True, check=False)
    except OSError as error:
        raise CantRun(f"{argv[0]} can't start: {error}") from None
    return Ran(done.returncode, done.stdout, done.stderr)


def checked(host: Host, argv: Sequence[str], cwd: str, fault: type[Exception], what: str) -> Ran:
    """Runs a command of git or gh through the host, as one that must give 0.

    Takes: the host, the command's words and the folder to run it in, as `run` takes them, the
    fault to raise, such as CantRun or Missing, and what the command does, for the message.
    Gives: what it gave, where it gives 0.
    Changes: whatever the command changes.
    Refuses: the fault as `<what>: <what the command printed>`, where it gives other than 0.
    """
    ran = host(argv, cwd)
    if ran.code != 0:
        raise fault(f"{what}: {(ran.out + ran.err).strip()}")
    return ran
