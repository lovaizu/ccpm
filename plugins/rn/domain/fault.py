"""Decides how each of rn's commands, tree.py and record.py, says what stopped it, as repository
raises it to tree.py too: a fault of the input that whoever ran it can mend, a thing outside the
work that's missing, or a check that couldn't run."""

from __future__ import annotations


class Wrong(Exception):
    """An input from outside that a command refuses, such as a file out of its form, said so that
    whoever ran the command can mend it: which file or argument, what's wrong, and what it takes.
    The command gives 1."""


class Missing(Exception):
    """Something outside the work that a command needs and doesn't find, such as a login of gh or a
    remote to push to, said so that the user can clear it. The command gives 1."""


class CantRun(Exception):
    """What kept a command from doing what it names, such as a file it couldn't read, so that it
    passes nothing it didn't check. The command gives 2."""
