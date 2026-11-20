"""Decides where the folder of the people's starting state lies and what it holds, in which an
evaluator tries a deliverable: a folder named by its Round in the system's temporary folder,
holding the work's branch as its people would get it, and nothing of how rn made it."""

from __future__ import annotations

from rounds.files import Round

from repository.host import Host
from repository.place import RunPlace


def folder(run: RunPlace, round_: Round) -> str:
    """Where the Round's evaluator tries its deliverable.

    Takes: the run, and the Round.
    Gives: the absolute path `<tempfile.gettempdir()>/rn-trial-<run's name>-<Round's folder's
    name within the run's Rounds, each `/` as `-`>/`, the same for each call, so that Lane's
    rules of the evaluator's start name it before it's made.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("repository.trial.folder")


def starting_state(run: RunPlace, round_: Round, host: Host) -> str:
    """Makes the folder in which the Round's evaluator tries its deliverable as its people would.

    Takes: the run, the Round, and the host.
    Gives: the folder's absolute path, as `folder` gives it.
    Changes: makes the folder anew, removing one left there, holding a clone of the work's branch
    at the worktree's files as they stand, the uncommitted ones among them, without `.rn/`.
    Refuses: CantRun where git can't clone or the folder can't be made, with what went wrong.
    """
    raise NotImplementedError("repository.trial.starting_state")
