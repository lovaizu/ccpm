"""Decides the steps of stacking a queue: what the stacker asks before it takes the queue in, and
what it writes and starts once it does."""

from __future__ import annotations

from runner.handoff import Handoff


def stack(path: str) -> Handoff:
    """The queue at `path`, taken in and set going.

    Takes: the queue file's absolute path.
    Gives: what the runner was handed: the queue file's path, the queue's start, and the tasks that
    the runner carries, the ones that didn't finish, each with its session.
    Changes: the queue's record, where each task that didn't finish waits for the start with its
    session kept, and starts the queue's runner apart from Claude Code by `stacker.detach`, handing
    it the queue's start and those tasks with their sessions.
    Refuses:
    - stacker.queue_file.Refused, with each fault, where the file can't be read as a queue or a
      task can't start, writing and starting nothing;
    - ValueError, naming the file and what's wrong, where the queue's runs' file leaves its form,
      writing and starting nothing;
    - OSError, with what the OS said, where the queue's record can't be written, starting nothing;
    - stacker.detach.CantStart, with what the OS said, where the OS doesn't start the runner, the
      record left written, so that stacking the queue again carries each task on.
    """
    raise NotImplementedError("stacker.stack.stack")
