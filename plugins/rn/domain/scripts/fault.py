"""Decides how each of rn's commands says what stopped it: a fault of the input that whoever ran it
can mend, a thing outside the work that's missing, or a check that couldn't run; and how each ends,
with what it prints and the exit code it gives."""

from __future__ import annotations

import sys
import traceback
from typing import Callable, NoReturn

# What a command's `main` gives: the exit code, what goes to stdout, and what goes to stderr.
Answer = tuple[int, str, str]


class Wrong(Exception):
    """An input from outside that a command refuses, such as a file out of its form, said so that
    whoever ran the command can mend it: which file or argument, what's wrong, and what it takes.
    The command gives 1."""


class Missing(Exception):
    """Something outside the work that a command needs and doesn't find, such as a git repository
    or a remote to push to, said so that the user can clear it. The command gives 1."""


class CantRun(Exception):
    """What kept a command from doing what it names, such as a file it couldn't read, so that it
    passes nothing it didn't check. The command gives 2."""


def answered(script: str, call: Callable[[], Answer]) -> Answer:
    """What the call gives, or, where it raises, the exit code of the fault with
    `<script>: <what's wrong>`: 1 where the input is Wrong or something is Missing, and 2 where it
    CantRun."""
    try:
        return call()
    except (Wrong, Missing) as wrong:
        return 1, "", f"{script}: {wrong}\n"
    except CantRun as stopped:
        return 2, "", f"{script}: {stopped}\n"


def end(main: Callable[[], Answer]) -> NoReturn:
    """Ends the command with what its `main` gave: the exit code, what goes to stdout, and what
    goes to stderr. Where `main` raises an error that no fault names, it ends with 2 and the
    error's traceback on stderr, as the role that ran it reads 1 as a fault of its input to mend
    and 2 as a check that couldn't check, which a rerun checks no more."""
    try:
        code, printed, said = main()
    except Exception:  # noqa: BLE001 - the entry of each command, where any error ends it.
        code, printed, said = 2, "", traceback.format_exc()
    sys.stdout.write(printed)
    sys.stderr.write(said)
    raise SystemExit(code)
