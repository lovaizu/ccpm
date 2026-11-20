"""Decides what each role's Cut holds: for the generator, the deliverable, its kind's or the
refactor best practice, the goal, and the decisions of its node and of each input node with no
file; for an evaluator, the deliverable, its people's aim, and the conditions of its group. The
deliverable holds its name, path, and kind, and its more_paths where the node has them."""

from __future__ import annotations

import json
import os
from typing import Any

from fault import Wrong

from tree import course, rounds
from tree.course import Due
from tree.design import Tree


def write(run: str, tree: Tree, due: Due) -> str:
    """Writes the Cut of a start due.

    Takes: the run's folder, the design tree, and the start due.
    Gives: the path of the Cut written, in a slot of its own that rounds.fresh names, as a start
    that didn't end leaves its Cut with no result, which counts for nothing.
    Changes: the run's folder, by the Cut, in the form of `schemas/cut.schema.json`.
    Refuses: Wrong where the start names a deliverable or a group that the tree doesn't hold."""
    path = rounds.fresh(run, rounds.Start(due.round, due.role, due.group, {}, None))
    node = next((d for d in tree["deliverables"] if d["path"] == due.deliverable), None)
    if node is None:
        raise Wrong(f"no deliverable {due.deliverable} is in the design tree to cut a start of")
    held: dict[str, Any] = {
        "role": due.role,
        "deliverable": {k: node[k] for k in ("name", "path", "kind", "more_paths") if k in node},
        "best_practice": due.best_practice,
        "goal": tree["goal"]["decided"],
    }
    if due.role == "generator":
        held["decisions"] = course.decisions(tree, due.deliverable)
    else:
        conditions = course.groups(due.best_practice).get(due.group)
        if conditions is None:
            raise Wrong(f"the {due.best_practice} best practice has no group {due.group}")
        held.update(group=due.group, conditions=list(conditions))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(held, f, indent=2)
        f.write("\n")
    return path
