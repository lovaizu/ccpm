"""Decides what `queue.py run` takes and the exit code it ends with, as a program that no one
watches."""

from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str], stdin: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `queue.py run` with the arguments and what came on its
    standard input.

    Takes: the arguments after `queue.py run`, and the text of its standard input.
    Gives: for no arguments, and the queue on its standard input as `runner.handoff.encode` gives
    it, 0 once each task has ended, by `runner.schedule.carry`. 1 with what's wrong where the input
    isn't in that form, or another runner holds the queue's lock. 2 with the usage where it's given
    arguments.
    Changes: what `runner.schedule.carry` changes.
    Refuses: nothing, as each refusal gives its exit code.
    """
    raise NotImplementedError("runner.command.main")
