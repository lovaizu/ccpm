"""Decides where a run lies and what it's called: its name from the day and a slug of the work, the
worktree it works in, its folder there, and the paths of its steering, the pruner's result, and its
Rounds and Fixes in that folder."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date

from fault import Wrong

# A run's slug: one to five words of lower-case English letters and digits, joined by `-`, short
# enough to read in a folder's name.
_SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+){0,4}")
# A run's folder, `<worktree>/.rn/<name>`.
_FOLDER = re.compile(r"(.+)/\.rn/([0-9]{8}-[a-z0-9]+(?:-[a-z0-9]+){0,4})")


@dataclass(frozen=True)
class RunPlace:
    """One run of rn, by the worktree it works in and its name, `<yyyymmdd>-<slug>`, from which
    each of its paths follows."""

    worktree: str
    name: str

    @property
    def folder(self) -> str:
        """The run's folder in its worktree, `<worktree>/.rn/<name>/`."""
        return os.path.join(self.worktree, ".rn", self.name)

    @property
    def steering(self) -> str:
        """The run's steering, `<folder>/steering.json`."""
        return os.path.join(self.folder, "steering.json")

    @property
    def pruner(self) -> str:
        """The pruner's result, `<folder>/pruner.json`, which no commit holds."""
        return os.path.join(self.folder, "pruner.json")

    @property
    def rounds(self) -> str:
        """The folder of the run's Rounds and Fixes, `<folder>/rounds/`."""
        return os.path.join(self.folder, "rounds")


def named(today: date, slug: str) -> str:
    """The name of a run started on the day.

    Takes: the day, and a short English slug of the work, such as `see-it-work-early`.
    Gives: `<yyyymmdd>-<slug>`.
    Changes: nothing.
    Refuses: Wrong where the slug isn't one to five words of lower-case English letters and
    digits joined by `-`, naming it and that form.
    """
    if not _SLUG.fullmatch(slug):
        raise Wrong(
            f"the slug {slug!r} isn't a run's name; give one to five lower-case English words"
            " joined by -, such as see-it-work-early"
        )
    return f"{today:%Y%m%d}-{slug}"


def of_folder(cwd: str, folder: str) -> RunPlace:
    """The run whose folder a script is given.

    Takes: the folder that the command runs in, and the run's folder, from it or absolute, as
    `<worktree>/.rn/<name>`.
    Gives: the run.
    Changes: nothing.
    Refuses: Wrong where the path isn't a run's folder of that form, or no such folder lies there,
    naming the path and the form it takes.
    """
    path = os.path.normpath(os.path.join(cwd, folder))
    found = _FOLDER.fullmatch(path)
    if not found:
        raise Wrong(f"{folder}: isn't a run's folder, which takes the form <worktree>/.rn/<name>")
    if not os.path.isdir(path):
        raise Wrong(f"{folder}: no such folder; give the run's folder as made")
    return RunPlace(found[1], found[2])
