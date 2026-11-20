"""Decides where a run lies and what it's called: its name from the day and the goal, its worktree
and branch, its folder, and the paths of its design tree and its Rounds in that folder."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date

from fault import Wrong

# The most words of the goal that a run's name takes.
_WORDS = 5
# A run's folder, `<repository>/.claude/worktrees/rn-<name>/.rn/<name>`.
_FOLDER = re.compile(r"(.+)/\.claude/worktrees/rn-([^/]+)/\.rn/([^/]+)")
_FORM = "<repository>/.claude/worktrees/rn-<name>/.rn/<name>"


@dataclass(frozen=True)
class RunPlace:
    """One run of rn in the user's repository, by the repository's top and the run's name,
    `<yyyymmdd>-<goal>`, from which each of its paths follows."""

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


def named(today: date, goal: str) -> str:
    """The name of a run started on the day toward the goal.

    Takes: the day, and the goal in the user's words, as typed after `/rn:up`.
    Gives: `<yyyymmdd>-<goal>`, the goal as at most five of its words, lower case, joined by `-`,
    with each character other than a letter or a digit left out.
    Changes: nothing.
    Refuses: Wrong where the goal holds no letter or digit, saying that `/rn:up` takes what the
    user wants in words.
    """
    if not any(each.isalnum() for each in goal):
        raise Wrong(
            f"the goal {goal!r} holds no letter or digit; /rn:up takes what the user wants in words"
        )
    words = ["".join(each for each in word if each.isalnum()).lower() for word in goal.split()]
    return f"{today:%Y%m%d}-{'-'.join(words[:_WORDS])}"


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
