"""Decides where the folder of the people's starting state lies and what it holds, in which an
evaluator tries a deliverable: a folder named by its Round in the system's temporary folder,
holding the work's branch as its people would get it, and nothing of how rn made it."""

from __future__ import annotations

import os
import shutil
import tempfile

from fault import CantRun, Wrong
from host import Host, checked
from place import WorkPlace
from push import branch


def folder(work: WorkPlace, round_: str) -> str:
    """Where the Round's evaluator tries its deliverable.

    Takes: the work, and the Round's folder, absolute.
    Gives: the absolute path `<tempfile.gettempdir()>/rn-trial-<work's name>-<Round's folder's
    path within the work's Rounds, each `/` as `-`>/`, the same for each call.
    Changes: nothing.
    Refuses: Wrong where the folder doesn't lie within the work's Rounds, naming it.
    """
    within = os.path.relpath(os.path.normpath(round_), work.rounds)
    if within == os.curdir or within.startswith(os.pardir):
        raise Wrong(f"{round_}: isn't a Round's folder within {work.rounds}")
    within = within.replace(os.sep, "-")
    return os.path.join(tempfile.gettempdir(), f"rn-trial-{work.name}-{within}") + os.sep


def starting_state(work: WorkPlace, round_: str, host: Host) -> str:
    """Makes the folder in which the Round's evaluator tries its deliverable as its people would.

    Takes: the work, the Round's folder, absolute, and the host.
    Gives: the folder's absolute path, as `folder` gives it.
    Changes: makes the folder anew, removing one left there, holding a clone of the work's branch
    as committed, as rn's hook commits each role's changes once it ends, without `.rn/`.
    Refuses: CantRun where git can't clone, with what it said.
    """
    made = folder(work, round_)
    if os.path.exists(made):
        shutil.rmtree(made)
    clone = ["git", "clone", "-q", "--branch", branch(work, host), work.worktree, made]
    checked(host, clone, work.worktree, CantRun, f"git can't clone the work's branch into {made}")
    shutil.rmtree(os.path.join(made, ".rn"), ignore_errors=True)
    return made
