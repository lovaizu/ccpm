"""Decides which start due a new start of a role takes: `cut.py <role> [<Cut>...]`, which the
orchestrator runs for each start that Lane gives due, naming the Cut of each start of the role that
runs. It writes the Cut of the first start due of the role, in the course's order, that none of
those holds, and prints its path, which the start's prompt names."""

from __future__ import annotations

import json
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
USAGE = "usage: cut.py generator|evaluator [<Cut of each start of the role that runs>...]\n"


def main(argv: list[str], cwd: str) -> tuple[int, str, str]:
    """Writes the Cut of a start due through course.due and cut.write.

    Takes: the role, then the path of the Cut of each start of the role that runs, from the top of
    the run's worktree; and that worktree.
    Gives: 0 with the path of the Cut, from the worktree's top, on a line; 1 with what Wrong says,
    such as a worktree that holds no run, or where no start of the role is due beside those that
    run; 2 with the usage where the first argument isn't a role.
    Changes: the run's folder, by the Cut written, where none is there yet for the start."""
    if not argv or argv[0] not in ROLES:
        return 2, "", USAGE
    role = argv[0]
    try:
        run = _run(cwd)
        tree = design.read(os.path.join(cwd, run), PLUGIN)
        running = [_due(cwd, each) for each in argv[1:]]
        due = course.due(tree, rounds.each(os.path.join(cwd, run)), running)
    except Wrong as wrong:
        return 1, "", f"cut.py: {wrong}\n"
    mine = [d for d in due if d.role == role]
    if not mine:
        return 1, "", f"cut.py: no start of the {role} is due beside those that run\n"
    path = os.path.relpath(cut.write(os.path.join(cwd, run), tree, mine[0]), cwd)
    return 0, f"{path}\n", ""


def _run(cwd: str) -> str:
    """The run's folder from the top of the worktree, as the orchestrator runs this in the run's
    worktree."""
    found = rounds.folder(cwd)
    if found is None:
        raise Wrong(f"{cwd} holds no run's design tree in .rn/; start the run with /rn:up")
    return found


def _due(cwd: str, path: str) -> course.Due:
    """The start that runs, as its Cut names it."""
    with open(os.path.join(cwd, path), encoding="utf-8") as f:
        held = json.load(f)
    return course.Due(
        held["deliverable"]["path"],
        held["role"],
        held.get("group", ""),
        held["best_practice"],
        int(path.split("/")[-2]),
    )


if __name__ == "__main__":
    end(main(sys.argv[1:], os.getcwd()))
