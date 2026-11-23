"""Decides how overnight tells where a queue's tasks stand: how many finished and how many were
given up, and each task's end, wait, reply, folder written in, and why given up."""

from __future__ import annotations

from record.store import Standing


def tell(queue_file: str, standing: Standing) -> str:
    """The text that tells where the queue's tasks stand, as the README's walkthrough shows.

    Takes: the queue file's absolute path, and where its tasks stand.
    Gives: the count of tasks finished and given up, then each task's end, its wait for the limit,
    its reply's path, the folder it wrote in, and why it was given up, with how to carry on the
    tasks that a stop left, by stacking the queue again.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("checker.report.tell")


def unnamed(version: str) -> str:
    """The text for a check that names no queue that was stacked.

    Takes: overnight's version, such as `0.1.0`.
    Gives: the version and what to name, such as `overnight 0.1.0: name the queue file to check`.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("checker.report.unnamed")
