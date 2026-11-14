"""Decides where a deliverable's commands run: in a throwaway copy of the run's worktree, as it
stands with the work not yet committed, with a throwaway home folder, both in `<temp>/rn/<run>/` of
the system's temporary folder, so that no command reaches the user's own files.
`throwaway.py try <run> <deliverable> <round> <command>` runs the command there and keeps it in the
round's Try record."""

from __future__ import annotations

from collections.abc import Mapping

from tree.rounds import Tried

USAGE = "usage: throwaway.py try <run> <deliverable> <round> <command>"


def copy(worktree: str, run_name: str) -> tuple[str, str]:
    """Makes a fresh throwaway copy of the worktree, with its files as they stand, and an empty
    home folder beside it, in the system's temporary folder, and gives the copy's path and the
    home's."""
    raise NotImplementedError("throwaway.copy")


def run(command: str, copy: str, home: str, environ: Mapping[str, str]) -> Tried:
    """Runs the shell command in the copy, with HOME the home folder and nothing else of the
    environment changed, and gives what it printed and its exit code."""
    raise NotImplementedError("throwaway.run")


def main(argv: list[str], environ: Mapping[str, str], cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `throwaway.py` with the arguments, from the run's
    worktree `cwd`: for `try`, the command's own exit code and what it printed, once the Try record
    of the round keeps it; 1 where the deliverable or the round isn't one the run has; 2 with the
    usage where the arguments are no `try` of four."""
    raise NotImplementedError("throwaway.main")
