"""Decides where the work lies in the worktree that rn runs in, and how it's found again: its
folder made at the worktree's top, and each folder of work there found, newest first."""

from __future__ import annotations

import json
import os
import re

import form
from fault import Missing, Wrong
from host import Host
from place import WorkPlace
from steering.due import due

# The name of a piece of work's folder, as `place.named` gives it.
_NAME = re.compile(r"[0-9]{8}-[a-z0-9]+(?:-[a-z0-9]+){0,4}")


def top(cwd: str, host: Host) -> str:
    """The top of the worktree that the folder lies in.

    Takes: a folder, and the host.
    Gives: the worktree's top, as git names it.
    Changes: nothing.
    Refuses: Missing where the folder lies in no git worktree.
    """
    shown = host(["git", "rev-parse", "--show-toplevel"], cwd)
    if shown.code != 0:
        raise Missing(f"{cwd} lies in no git worktree; start rn in the worktree of the work")
    return shown.out.strip()


def new(work: WorkPlace) -> WorkPlace:
    """Makes the work's folder at its worktree's top.

    Takes: the work to make, its worktree the one rn runs in, and its name by `place.named`.
    Gives: the work, made.
    Changes: makes the work's folder, empty, for the work's first aim.
    Refuses: Wrong where work of the name already lies there.
    """
    if os.path.exists(work.folder):
        raise Wrong(f"the work {work.name} already lies at {work.folder}; pick it up with /rn:up")
    os.makedirs(work.folder)
    return work


def works(cwd: str, host: Host) -> list[WorkPlace]:
    """rn's work in the worktree that the folder lies in.

    Takes: a folder, and the host.
    Gives: each piece of work whose folder lies in the worktree's `.rn/`, newest first by its
    name; none where the folder lies in no git worktree.
    Changes: nothing.
    Refuses: nothing.
    """
    try:
        worktree = top(cwd, host)
    except Missing:
        return []
    folder = os.path.join(worktree, ".rn")
    names = os.listdir(folder) if os.path.isdir(folder) else []
    found = [
        each
        for each in names
        if _NAME.fullmatch(each) and os.path.isdir(os.path.join(folder, each))
    ]
    return [WorkPlace(worktree, each) for each in sorted(found, reverse=True)]


def left(cwd: str, host: Host, schema: str) -> list[WorkPlace]:
    """Each piece of work with something left to do, as `works` gives it, whose steering has
    something due other than its end, or that has no steering yet. A work whose steering leaves
    the steering's schema at `schema` is an earlier rn's, which this rn doesn't go on with, as the
    work ended keeps its folder in the repository once its pull request is merged.

    Refuses: Wrong where the work's steering isn't JSON, naming its path.
    """
    return [each for each in works(cwd, host) if _open(each, schema)]


def _open(work: WorkPlace, schema: str) -> bool:
    """Whether the work has something left to do: no steering yet, or one in this rn's form with
    something due but its end."""
    if not os.path.isfile(work.steering):
        return True
    with open(work.steering, encoding="utf-8") as f:
        try:
            steering = json.load(f)
        except ValueError as error:
            raise Wrong(f"{work.steering}: isn't JSON: {error}") from None
    return not form.faults(steering, schema) and due(steering) != ["ended"]
