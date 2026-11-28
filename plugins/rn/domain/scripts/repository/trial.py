"""Decides where the folder of the people's starting state lies and what it holds, in which an
evaluator tries a deliverable: a folder named by its Round in the system's temporary folder,
holding the work as it stands in its worktree, as its people would get it, and nothing of how rn
made it, removed once the role that tried it ends."""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile

from fault import CantRun, Wrong
from host import Host, checked
from place import WorkPlace


def folder(work: WorkPlace, round_: str) -> str:
    """Where the Round's evaluator tries its deliverable.

    Takes: the work, and the Round's folder, absolute.
    Gives: the absolute path `<tempfile.gettempdir()>/rn-trial-<work's name>/<Round's folder's
    path within the work's tasks, each `/` as `-`>/`, the same for each call.
    Changes: nothing.
    Refuses: Wrong where the folder doesn't lie within the work's tasks, naming it.
    """
    within = os.path.relpath(os.path.normpath(round_), work.tasks)
    if within == os.curdir or within.startswith(os.pardir):
        raise Wrong(f"{round_}: isn't a Round's folder within {work.tasks}")
    within = within.replace(os.sep, "-")
    return os.path.join(_trials(work), within) + os.sep


def starting_state(work: WorkPlace, round_: str, host: Host) -> str:
    """Makes the folder in which the Round's evaluator tries its deliverable as its people would.

    Takes: the work, the Round's folder, absolute, and the host.
    Gives: the folder's absolute path, as `folder` gives it.
    Changes: makes the folder anew, removing one left there, holding a clone of the work's
    worktree with each change in it not yet committed, as the orchestrator commits only at the end
    of a purpose, and without `.rn/`.
    Refuses: CantRun where git can't clone or list the changes, with what it said.
    """
    made = folder(work, round_)
    if os.path.exists(made):
        shutil.rmtree(made)
    clone = ["git", "clone", "-q", work.worktree, made]
    checked(host, clone, work.worktree, CantRun, f"git can't clone the work's worktree into {made}")
    _changes_copied(work, made, host)
    shutil.rmtree(os.path.join(made, ".rn"), ignore_errors=True)
    return made


def _changes_copied(work: WorkPlace, made: str, host: Host) -> None:
    """Copies each file of the worktree that changed or is new since its last commit into the
    clone, and removes each that's gone from it since, staged or not, as a rename staged by
    `git mv` is, leaving out what git ignores."""
    what = "git can't list the worktree's changes"
    since = ["git", "diff", "-z", "--name-only", "--no-renames", "HEAD"]
    others = ["git", "ls-files", "-z", "--others", "--exclude-standard"]
    changed = checked(host, since, work.worktree, CantRun, what).out.split("\0")
    changed += checked(host, others, work.worktree, CantRun, what).out.split("\0")
    for each in filter(None, changed):
        target = os.path.join(made, each)
        if not os.path.lexists(os.path.join(work.worktree, each)):
            with contextlib.suppress(FileNotFoundError):
                os.remove(target)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(os.path.join(work.worktree, each), target)


def removed(work: WorkPlace) -> None:
    """Removes each folder that a Round of the work tried its deliverable in.

    Takes: the work.
    Gives: nothing.
    Changes: removes the folder that holds each folder `folder` names for the work, as no role
    tries in it once its role ends.
    Refuses: nothing.
    """
    shutil.rmtree(_trials(work), ignore_errors=True)


def _trials(work: WorkPlace) -> str:
    """The folder of the work's trials, in the system's temporary folder."""
    return os.path.join(tempfile.gettempdir(), f"rn-trial-{work.name}")
