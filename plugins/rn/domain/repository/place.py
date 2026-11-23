"""Decides where a run lies and what it's called: its name from the day and a slug of the work, its
worktree and branch, its folder, the paths of its design tree and its Rounds in that folder, and
which run a conversation works on."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date

from fault import Wrong

# A run's slug: one to five words of lower-case English letters and digits, joined by `-`.
_SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+){0,4}")
# A run's folder, `<repository>/.claude/worktrees/rn-<name>/.rn/<name>`.
_FOLDER = re.compile(r"(.+)/\.claude/worktrees/rn-([^/]+)/\.rn/([^/]+)")
_FORM = "<repository>/.claude/worktrees/rn-<name>/.rn/<name>"
# A run's worktree's folder name, `rn-<yyyymmdd>-<slug>`.
_WORKTREE = re.compile(r"rn-(\d{8})-(.+)")


@dataclass(frozen=True)
class RunPlace:
    """One run of rn in the user's repository, by the repository's top and the run's name,
    `<yyyymmdd>-<slug>`, from which each of its paths follows."""

    repository: str
    name: str

    @property
    def worktree(self) -> str:
        """The run's own worktree, `<repository>/.claude/worktrees/rn-<name>/`."""
        return os.path.join(self.repository, ".claude", "worktrees", self.branch)

    @property
    def branch(self) -> str:
        """The work's branch, which the worktree has checked out, `rn-<name>`."""
        return f"rn-{self.name}"

    @property
    def folder(self) -> str:
        """The run's folder on the work's branch, `<worktree>/.rn/<name>/`."""
        return os.path.join(self.worktree, ".rn", self.name)

    @property
    def tree(self) -> str:
        """The run's design tree, `<folder>/design-tree.json`."""
        return os.path.join(self.folder, "design-tree.json")

    @property
    def rounds(self) -> str:
        """The folder of the run's Rounds, `<folder>/rounds/`."""
        return os.path.join(self.folder, "rounds")

    def holds(self, path: str) -> bool:
        """Whether the path, from the worktree's top, lies inside the worktree."""
        within = os.path.normpath(os.path.join(self.worktree, path))
        return within.startswith(os.path.normpath(self.worktree) + os.sep)


def named(today: date, slug: str) -> str:
    """The name of a run started on the day.

    Takes: the day, and a short English slug of the work, as the orchestrator writes it from the
    issue's title where the request names an issue, else from the request's words, such as
    `overnight-claude-p-queue` for issue #62.
    Gives: `<yyyymmdd>-<slug>`.
    Changes: nothing.
    Refuses: Wrong where the slug isn't one to five words of lower-case English letters and
    digits joined by `-`, naming it and that form.
    """
    if not _SLUG.fullmatch(slug):
        raise Wrong(
            f"the slug {slug!r} isn't a run's name; give one to five lower-case English words"
            " joined by -, from the issue's title or the request's words, such as"
            " overnight-claude-p-queue"
        )
    return f"{today:%Y%m%d}-{slug}"


def of_folder(cwd: str, folder: str) -> RunPlace:
    """The run whose folder a script or a role is given.

    Takes: the folder that the command runs in, and the run's folder, from it or absolute, as
    `<repository>/.claude/worktrees/rn-<name>/.rn/<name>`.
    Gives: the run.
    Changes: nothing.
    Refuses: Wrong where the path isn't a run's folder of that form, or holds no design tree,
    naming the path and the form it takes.
    """
    path = os.path.normpath(os.path.join(cwd, folder))
    found = _FOLDER.fullmatch(path)
    if not found or found[2] != found[3]:
        raise Wrong(f"{folder}: isn't a run's folder, which takes the form {_FORM}")
    run = RunPlace(found[1], found[2])
    if not os.path.isfile(run.tree):
        raise Wrong(f"{folder}: holds no design tree, design-tree.json, as a run's folder does")
    return run
