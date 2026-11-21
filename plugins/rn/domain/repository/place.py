"""Decides where a run lies and what it's called: its name from the day and the goal, its worktree
and branch, its folder, the paths of its design tree and its Rounds in that folder, and which run a
request's words named."""

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
# A run's worktree's folder name, `rn-<yyyymmdd>-<goal>`.
_WORKTREE = re.compile(r"rn-(\d{8})-(.+)")


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

    def holds(self, path: str) -> bool:
        """Whether the path, from the worktree's top, lies inside the worktree."""
        within = os.path.normpath(os.path.join(self.worktree, path))
        return within.startswith(os.path.normpath(self.worktree) + os.sep)


def named(today: date, goal: str) -> str:
    """The name of a run started on the day toward the goal.

    Takes: the day, and the goal in the user's words, as typed in reply to `/rn:on`.
    Gives: `<yyyymmdd>-<goal>`, the goal as at most five of its words, lower case, joined by `-`,
    with each character other than a letter or a digit left out.
    Changes: nothing.
    Refuses: Wrong where the goal holds no letter or digit, saying that `/rn:on` takes what the
    user wants in words.
    """
    return f"{today:%Y%m%d}-{_goal(goal)}"


def _goal(words: str) -> str:
    """The goal's part of a run's name, refused as `named` refuses the words."""
    if not any(each.isalnum() for each in words):
        raise Wrong(
            f"the goal {words!r} holds no letter or digit;"
            " /rn:on takes what the user wants in words"
        )
    kept = ["".join(each for each in word if each.isalnum()).lower() for word in words.split()]
    return "-".join(kept[:_WORDS])


def made(repository: str, words: str) -> RunPlace | None:
    """The run that a request of the words made in the repository, on whichever day it was made.

    Takes: the top of the user's repository, and the user's words in reply to `/rn:on`.
    Gives: the run whose name `named` gives from the words on some day, and whose design tree lies
    in its worktree here, the latest day's where several do, as a request made before midnight
    and answered after it names its run by the day before; None where none does.
    Changes: nothing.
    Refuses: Wrong as `named` refuses the words.
    """
    goal = _goal(words)
    worktrees = os.path.join(repository, ".claude", "worktrees")
    folders = os.listdir(worktrees) if os.path.isdir(worktrees) else []
    matched = [_WORKTREE.fullmatch(each) for each in folders]
    days = sorted((each[1] for each in matched if each and each[2] == goal), reverse=True)
    runs = [RunPlace(repository, f"{day}-{goal}") for day in days]
    return next((run for run in runs if os.path.isfile(run.tree)), None)


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
