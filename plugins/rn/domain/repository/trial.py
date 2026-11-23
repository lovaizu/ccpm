"""Decides where the folder of the people's starting state lies and what it holds, in which an
evaluator tries a deliverable: a folder named by its Round in the system's temporary folder,
holding the work's branch as its people would get it, and nothing of how rn made it."""

from __future__ import annotations

import os
import shutil
import tempfile
from typing import Callable

from fault import CantRun
from rounds.files import Round

from repository.host import Host, checked
from repository.place import RunPlace


def folder(run: RunPlace, round_: Round) -> str:
    """Where the Round's evaluator tries its deliverable.

    Takes: the run, and the Round.
    Gives: the absolute path `<tempfile.gettempdir()>/rn-trial-<run's name>-<Round's folder's
    name within the run's Rounds, each `/` as `-`>/`, the same for each call.
    Changes: nothing.
    Refuses: nothing.
    """
    within = os.path.relpath(round_.folder, run.rounds).replace(os.sep, "-")
    return os.path.join(tempfile.gettempdir(), f"rn-trial-{run.name}-{within}") + os.sep


def starting_state(run: RunPlace, round_: Round, host: Host) -> str:
    """Makes the folder in which the Round's evaluator tries its deliverable as its people would.

    Takes: the run, the Round, and the host.
    Gives: the folder's absolute path, as `folder` gives it.
    Changes: makes the folder anew, removing one left there, holding a clone of the work's branch
    at the worktree's files as they stand, the uncommitted ones among them, without `.rn/`.
    Refuses: CantRun where git can't clone or the folder can't be made, with what went wrong.
    """
    made = folder(run, round_)
    if os.path.exists(made):
        shutil.rmtree(made)
    clone = ["git", "clone", "-q", "--branch", run.branch, run.worktree, made]
    checked(host, clone, run.worktree, CantRun, f"git can't clone the work's branch into {made}")
    for name in os.listdir(made):
        if name != ".git":
            _remove(os.path.join(made, name))
    shutil.copytree(run.worktree, made, ignore=_outside(run.worktree), dirs_exist_ok=True)
    return made


def _remove(path: str) -> None:
    """Removes the file or the folder."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def _outside(worktree: str) -> Callable[[str, list[str]], set[str]]:
    """What copytree leaves out of the people's folder: the worktree's git and rn's own folder."""

    def ignored(folder: str, names: list[str]) -> set[str]:
        return {".git", ".rn"} & set(names) if folder == worktree else set()

    return ignored
