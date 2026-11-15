"""Decides how a deliverable's command runs where it can't change the user's files: in a throwaway
copy of rn's worktree, with a throwaway home, each command tried kept in the round's Try record."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Tried:
    """One command tried: the command, its exit code, and what it printed to stdout and stderr."""

    command: str
    code: int
    out: str
    err: str


def main(argv: Sequence[str], cwd: str) -> tuple[int, str, str]:
    """Runs throwaway.py.

    Takes: the command line after `throwaway.py`, `<deliverable> <command>`, and the folder it runs
    in, which lies in a run's worktree.
    Gives, as the exit code, standard output, and standard error: the command's own, run by `sh -c`
    in a copy of the worktree with HOME set to a throwaway folder, both in the system's temporary
    folder and removed once it ends; 1, with what's wrong, where the folder lies in no run's
    worktree or the deliverable has no round; 2, with the usage.
    Changes: adds the Tried to the file that `tree.rounds.try_path` names.
    Refuses: as Gives says, by its exit code.
    Carries: S1 `G->>W: tries it (Try record)`.
    """
    raise NotImplementedError("throwaway.main")
