"""Decides how each of rn's commands says what stopped it: a fault of the input that whoever ran it
can mend, or a step that couldn't run; and how each ends, with what it prints and the exit code it
gives."""

from __future__ import annotations

import sys
import traceback
from typing import Callable, NoReturn

# What a command's `main` gives: the exit code, what goes to stdout, and what goes to stderr.
Answer = tuple[int, str, str]


class Wrong(Exception):
    """An input from outside that a command refuses, such as a file that isn't JSON, said so that
    whoever ran the command can mend it: which file or argument, what's wrong, and what it takes.
    The command gives 1."""


class CantRun(Exception):
    """What kept a command from doing what it names, such as git failing, so that it claims nothing
    it didn't do. The command gives 2."""


def answered(script: str, call: Callable[[], Answer]) -> Answer:
    """What the call gives, or, where it raises CantRun, 2 with `<script>: <what stopped it>`."""
    try:
        return call()
    except CantRun as stopped:
        return 2, "", f"{script}: {stopped}\n"


def end(main: Callable[[], Answer]) -> NoReturn:
    """Ends the command with what its `main` gave: the exit code, what goes to stdout, and what
    goes to stderr. Where `main` raises an error that no fault names, it ends with 2 and the
    error's traceback on stderr, as the role that ran it reads 1 as a fault of its input to mend
    and 2 as a step that couldn't run, which a rerun runs no better."""
    try:
        code, printed, said = main()
    except Exception:  # noqa: BLE001 - the entry of each command, where any error ends it.
        code, printed, said = 2, "", traceback.format_exc()
    sys.stdout.write(printed)
    sys.stderr.write(said)
    raise SystemExit(code)
