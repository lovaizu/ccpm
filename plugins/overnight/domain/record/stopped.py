"""Decides what a run becomes once the runner that carried it stopped: given up, where the run
hadn't ended, and waiting for the start, where its queue is stacked again."""

from __future__ import annotations

from datetime import datetime

from record.runs import Run


def left(run: Run, now: datetime) -> Run:
    """The run of a task whose runner stopped.

    Takes: the run, and the moment the record sees the stop at.
    Gives: the run given up, saying that overnight stopped before the task ended, with its session,
    where it hadn't ended; the run as it was otherwise.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("record.stopped.left")


def carried_on(run: Run) -> Run:
    """The run of a task whose queue is stacked again.

    Takes: the run, of a runner that no longer carries it.
    Gives: the run waiting for the start, with its session kept and its stops counted from zero,
    where it didn't finish; the run as it was where it did.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("record.stopped.carried_on")
