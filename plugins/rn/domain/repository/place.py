"""Decides where a run lies and what it's called: its name from the day and the goal, its worktree
and branch, its folder, and the paths of its design tree and its Rounds in that folder."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class RunPlace:
    """One run of rn in the user's repository, by the repository's top and the run's name,
    `<yyyymmdd>-<goal>`, from which each of its paths follows."""

    repository: str
    name: str

    @property
    def worktree(self) -> str:
        """The run's own worktree, `<repository>/.claude/worktrees/rn-<name>/`."""
        raise NotImplementedError("repository.place.RunPlace.worktree")

    @property
    def branch(self) -> str:
        """The work's branch, which the worktree has checked out, `rn-<name>`."""
        raise NotImplementedError("repository.place.RunPlace.branch")

    @property
    def folder(self) -> str:
        """The run's folder on the work's branch, `<worktree>/.rn/<name>/`."""
        raise NotImplementedError("repository.place.RunPlace.folder")

    @property
    def tree(self) -> str:
        """The run's design tree, `<folder>/design-tree.json`."""
        raise NotImplementedError("repository.place.RunPlace.tree")

    @property
    def rounds(self) -> str:
        """The folder of the run's Rounds, `<folder>/rounds/`."""
        raise NotImplementedError("repository.place.RunPlace.rounds")


def named(today: date, goal: str) -> str:
    """The name of a run started on the day toward the goal.

    Takes: the day, and the goal in the user's words, as typed after `/rn:up`.
    Gives: `<yyyymmdd>-<goal>`, the goal as at most five of its words, lower case, joined by `-`,
    with each character other than a letter or a digit left out.
    Changes: nothing.
    Refuses: Wrong where the goal holds no letter or digit, saying that `/rn:up` takes what the
    user wants in words.
    """
    raise NotImplementedError("repository.place.named")


def of_folder(cwd: str, folder: str) -> RunPlace:
    """The run whose folder a script or a role is given.

    Takes: the folder that the command runs in, and the run's folder, from it or absolute, as
    `<repository>/.claude/worktrees/rn-<name>/.rn/<name>`.
    Gives: the run.
    Changes: nothing.
    Refuses: Wrong where the path isn't a run's folder of that form, or holds no design tree,
    naming the path and the form it takes.
    """
    raise NotImplementedError("repository.place.of_folder")
