"""Decides what `queue.py stack` takes and prints, and the exit code by which the skill's AI reads
its result."""

from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str], cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `queue.py stack` with the arguments.

    Takes: the arguments after `queue.py stack`, and the absolute path of the folder it runs from.
    Gives: for one queue file, by its path from `cwd`, 0 with the tasks stacked, when they start,
    and how to check them, as the README's walkthrough shows. Where `stacker.stack.stack` refuses:
    1 with each fault of the queue and how to mend it, on stacker.queue_file.Refused; 1 with what's
    wrong, on ValueError; 2 with what the OS said, on OSError or stacker.detach.CantStart. 2 with
    the usage where the arguments are other than one queue file.
    Changes: what `stacker.stack.stack` changes.
    Refuses: nothing, as each refusal of `stacker.stack.stack` gives its exit code.
    """
    raise NotImplementedError("stacker.command.main")
