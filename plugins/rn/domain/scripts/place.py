"""Decides where a run lies and what it's called: its name from the day and a slug of the work, its
worktree and branch, its folder, and the paths of its steering, the pruner's result, and its
Rounds and Fixes in that folder."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date

from fault import Wrong

# A run's slug: one to five words of lower-case English letters and digits, joined by `-`, short
# enough to read in a branch's name.
_SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+){0,4}")
# A run's folder, `<repository>/.claude/worktrees/rn-<name>/.rn/<name>`.
_FOLDER = re.compile(r"(.+)/\.claude/worktrees/rn-([^/]+)/\.rn/([^/]+)")
_FORM = "<repository>/.claude/worktrees/rn-<name>/.rn/<name>"


@dataclass(frozen=True)
class RunPlace:
    """One run of rn in the user's repository, by the repository's top and the run's name,
    `<yyyymmdd>-<slug>`, from which each of its paths follows."""

    repository: str
    name: str

    @property
    def branch(self) -> str:
        """The work's branch, which the worktree has checked out, `rn-<name>`."""
        return f"rn-{self.name}"

    @property
    def worktree(self) -> str:
        """The run's own worktree, `<repository>/.claude/worktrees/rn-<name>/`."""
        return os.path.join(self.repository, ".claude", "worktrees", self.branch)

    @property
    def folder(self) -> str:
        """The run's folder on the work's branch, `<worktree>/.rn/<name>/`."""
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
    `<repository>/.claude/worktrees/rn-<name>/.rn/<name>`.
    Gives: the run.
    Changes: nothing.
    Refuses: Wrong where the path isn't a run's folder of that form, or no such folder lies there,
    naming the path and the form it takes.
    """
    path = os.path.normpath(os.path.join(cwd, folder))
    found = _FOLDER.fullmatch(path)
    if not found or found[2] != found[3]:
        raise Wrong(f"{folder}: isn't a run's folder, which takes the form {_FORM}")
    if not os.path.isdir(path):
        raise Wrong(f"{folder}: no such folder; give the run's folder as made")
    return RunPlace(found[1], found[2])
