"""Decides what `queue.py check` takes and prints, and the exit code by which the skill's AI reads
its result."""

from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str], cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `queue.py check` with the arguments.

    Takes: the arguments after `queue.py check`, the absolute path of the folder it runs from, and
    that of overnight's folder.
    Gives: for one queue file, by its path from `cwd`, 0 with where its tasks stand, by
    `checker.report.tell`. For no argument, or a queue file that was never stacked, 0 with
    overnight's version from `.claude-plugin/plugin.json` and what to name, by
    `checker.report.unnamed`. 1 with what's wrong where the queue's runs leave their form. 2 with
    the usage where it's given more than one argument.
    Changes: what `record.store.standing` changes.
    Refuses: nothing, as each refusal of the record gives its exit code.
    """
    raise NotImplementedError("checker.command.main")
