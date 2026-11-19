"""Decides which start due a new start of a role takes: `cut.py <role>`, which the orchestrator
runs for each start that Lane gives due. It writes the Cut of the first start due of the role, in
the course's order, whose Cut isn't written yet, or else of the first whose Cut has no result, and
prints its path, which the start's prompt names."""

from __future__ import annotations

import os
import sys

# The code lies in domain/, which comes on the import path ahead of this file's own folder, so
# that `cut` and `tree` name the code there and not this file.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "domain"))

from fault import Wrong, end
from tree import course, cut, design, rounds

# rn's folder, where the design tree's schema and the best practices lie.
PLUGIN = os.path.dirname(HERE)
ROLES = ("generator", "evaluator")
USAGE = "usage: cut.py generator|evaluator\n"


def main(argv: list[str], cwd: str) -> tuple[int, str, str]:
    """Writes the Cut of a start due through course.due and cut.write.

    Takes: the role, and the run's worktree.
    Gives: 0 with the path of the Cut, from the worktree's top, on a line; 1 with what Wrong says,
    such as a worktree that holds no run, or where no start of the role is due; 2 with the usage
    where the arguments aren't a role.
    Changes: the run's folder, by the Cut written, where none is there yet for the start."""
    if len(argv) != 1 or argv[0] not in ROLES:
        return 2, "", USAGE
    role = argv[0]
    try:
        run = os.path.join(cwd, _run(cwd))
        tree = design.read(run, PLUGIN)
        due = course.due(tree, rounds.each(run), [])
    except Wrong as wrong:
        return 1, "", f"cut.py: {wrong}\n"
    mine = [d for d in due if d.role == role]
    if not mine:
        return 1, "", f"cut.py: no start of the {role} is due\n"
    new = [d for d in mine if not os.path.isfile(_path(run, d))]
    path = os.path.relpath(cut.write(run, tree, (new or mine)[0]), cwd)
    return 0, f"{path}\n", ""


def _run(cwd: str) -> str:
    """The run's folder from the top of the worktree, as the orchestrator runs this in the run's
    worktree."""
    found = rounds.folder(cwd)
    if found is None:
        raise Wrong(f"{cwd} holds no run's design tree in .rn/; start the run with /rn:up")
    return found


def _path(run: str, due: course.Due) -> str:
    """Where the Cut of the start due lies."""
    return rounds.path(run, rounds.Start(due.round, due.role, due.group, {}, None))


if __name__ == "__main__":
    end(main(sys.argv[1:], os.getcwd()))
