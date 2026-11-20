"""Decides what waits for the user's sign-off, and what a sign-off changes in the design tree: the
plan once it's open with each condition good, and another deliverable once its Rounds are over,
wait, and once signed off each is done, the open decisions of the findings left being the
proposals the user signed off."""

from __future__ import annotations

import copy
from collections.abc import Mapping

from fault import Wrong
from rounds.course import Next

from tree.form import Tree

# The statuses of a deliverable not yet done.
_OPEN = ("open", "doing")


def waiting(tree: Tree, nexts: Mapping[str, Next]) -> str | None:
    """The deliverable that waits for the user's sign-off.

    Takes: the tree, and what each open deliverable that Rounds make waits on, by its path, as
    `rounds.course.next_of` gives it.
    Gives: the path of the plan, the deliverable of the kind `design-tree`, where it's open with
    each condition good; else of the first open deliverable in the tree's order whose `next_of` is
    the sign-off; None where none does.
    Changes: nothing.
    Refuses: nothing.
    """
    opened = [each for each in tree["deliverables"] if each["status"] in _OPEN]
    for each in opened:
        good = all(condition["good"] for condition in each["necessary_conditions"])
        if each["kind"] == "design-tree" and good:
            return each["path"]
    for each in opened:
        if each["path"] in nexts and nexts[each["path"]].waits_on == "sign-off":
            return each["path"]
    return None


def signed_off(tree: Tree, deliverable: str) -> Tree:
    """The design tree once the user signs the deliverable off.

    Takes: the tree, and the path of the deliverable that `waiting` names.
    Gives: the tree with the deliverable done, whatever its conditions, keeping its name, path,
    more_paths, and kind, or, for a node with no file, its necessary conditions too; and without
    each item of `work` that names it.
    Changes: nothing.
    Refuses: Wrong where no open deliverable has the path.
    """
    signed = copy.deepcopy(tree)
    deliverables = signed["deliverables"]
    for index, node in enumerate(deliverables):
        if node["path"] == deliverable and node["status"] in _OPEN:
            deliverables[index] = _done(node)
            signed["work"] = [each for each in signed["work"] if each["path"] != deliverable]
            return signed
    raise Wrong(f"{deliverable}: no open deliverable of the design tree has the path to sign off")


def _done(node: Tree) -> Tree:
    """The deliverable done: its one line, or, for a node with no file, with its conditions."""
    kept = ("name", "path", "more_paths", "kind")
    done = {key: node[key] for key in kept if key in node}
    done["status"] = "done"
    if "file" in node:
        done["file"] = False
        done["necessary_conditions"] = node["necessary_conditions"]
    return done
