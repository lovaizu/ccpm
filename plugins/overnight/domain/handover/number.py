"""Which number a new piece takes: the one after the highest that any record, branch, or
worktree of overnight holds."""

from __future__ import annotations


def next_number(repository: str) -> int:
    """The number of the next piece in the repository.

    Takes: the repository's root.
    Gives: one more than the highest of `pieces.record.highest` and `worktree.taken`.
    Changes: nothing.
    Refuses: what `worktree.taken` refuses.
    """
    raise NotImplementedError("handover.number.next_number")
