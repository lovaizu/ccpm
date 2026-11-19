"""Decides which start due a new start of a role takes: `cut.py <role>`, which the orchestrator
runs for each start that Lane gives due. Of the role's starts due, in the course's order, it takes
the one with the fewest Cuts with no result since its last Cut with one, the first on a tie, writes
a fresh Cut for it in a slot of its own, and prints its path, which the start's prompt names. It
needs to know no start that runs: each holds a Cut with no result, so the pick passes it over, and
Lane gives due only as many starts of the role as don't run.

Its known limit: where a start fails while others of its role run, each due start of the role holds
one Cut with no result, so the tie goes to the first, which may be one that runs. That costs one
wasted start, which the next pick mends, as the failed start then holds the fewest.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence

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
        starts = rounds.each(run)
    except Wrong as wrong:
        return 1, "", f"cut.py: {wrong}\n"
    mine = [d for d in course.due(tree, starts, []) if d.role == role]
    if not mine:
        return 1, "", f"cut.py: no start of the {role} is due\n"
    picked = min(mine, key=lambda d: _waiting(starts, d))
    path = os.path.relpath(cut.write(run, tree, picked), cwd)
    return 0, f"{path}\n", ""


def _run(cwd: str) -> str:
    """The run's folder from the top of the worktree, as the orchestrator runs this in the run's
    worktree."""
    found = rounds.folder(cwd)
    if found is None:
        raise Wrong(f"{cwd} holds no run's design tree in .rn/; start the run with /rn:up")
    return found


def _waiting(starts: Sequence[rounds.Start], due: course.Due) -> int:
    """How many Cuts of the start due's role, group, and deliverable have no result since the last
    of them with one."""
    waiting = 0
    for each in starts:
        if (each.role, each.group, each.cut["deliverable"]["path"]) == (
            due.role,
            due.group,
            due.deliverable,
        ):
            waiting = 0 if each.result is not None else waiting + 1
    return waiting


if __name__ == "__main__":
    end(main(sys.argv[1:], os.getcwd()))
