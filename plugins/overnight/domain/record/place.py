"""Decides where overnight keeps what it writes for a queue: the folder beside the queue file named
after it, with the runs, each task's reply, and the runner's lock."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Place:
    """The absolute paths of what overnight writes for one queue: its folder, its runs' file, and
    its runner's lock."""

    folder: str
    runs: str
    lock: str

    def reply(self, task: str) -> str:
        """The absolute path of the reply file of the task by its name.

        Takes: the task's name, such as `review-payments`.
        Gives: the path, such as `/home/dev/overnight/tonight/review-payments.md`.
        Changes: nothing.
        Refuses: nothing.
        """
        raise NotImplementedError("record.place.Place.reply")


def of(queue_file: str) -> Place:
    """Where overnight writes for the queue file at the absolute path `queue_file`.

    Takes: the queue file's absolute path, such as `/home/dev/overnight/tonight.json`.
    Gives: its place, such as the folder `/home/dev/overnight/tonight` with `runs.json` in it.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("record.place.of")
