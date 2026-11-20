"""Decides how the design tree is kept as a file: read and written as JSON in the form of the
design tree best practice's `design-tree.schema.json`, each node named by its JSON Pointer, and the
tree that a run starts from, with the goal as put and the plan as its own deliverable."""

from __future__ import annotations

import json
from typing import Any

from fault import CantRun, Wrong
from practice import Practice

# A design tree, in the form of domain/best-practices/design-tree/design-tree.schema.json.
Tree = dict[str, Any]
# A deliverable of the design tree: one of `done`, `done_no_file`, or `open` of its schema.
Deliverable = dict[str, Any]


def started(goal: str, plan: str, practice: Practice) -> Tree:
    """The design tree that a run starts from.

    Takes: the goal as the orchestrator puts it, one sentence with the user as its subject; the
    plan's path from the run's worktree, `.rn/<name>/design-tree.json`, the tree's own; and the
    design tree best practice.
    Gives: a tree whose goal is the sentence, `by` reasoning until the user confirms it; whose one
    deliverable is the plan, named by the goal, of the kind `design-tree`, at the plan's path, with
    no inputs, status open, and each necessary condition of the best practice in its order, good
    false, with no decision; and whose work is none.
    Changes: nothing.
    Refuses: Wrong where the goal is empty.
    """
    if not goal:
        raise Wrong("the goal is empty; the tree starts from the goal as one sentence")
    conditions = [
        {"id": condition["id"], "good": False, "decisions": []}
        for factor in practice["goal"]["critical_success_factors"]
        for condition in factor["necessary_conditions"]
    ]
    return {
        "goal": {"decided": goal, "by": "reasoning"},
        "deliverables": [
            {
                "name": goal,
                "path": plan,
                "kind": "design-tree",
                "inputs": [],
                "status": "open",
                "necessary_conditions": conditions,
            }
        ],
        "work": [],
    }


def read(path: str) -> Tree:
    """The design tree in the file.

    Takes: the path of a run's `design-tree.json`.
    Gives: the tree, as the file holds it, whatever its form, as `tree.checks` judges that.
    Changes: nothing.
    Refuses: Wrong where the file is missing or isn't JSON, naming it.
    """
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise Wrong(f"{path}: no design tree lies there") from None
    except ValueError as error:
        raise Wrong(f"{path}: isn't JSON: {error}") from None


def write(path: str, tree: Tree) -> None:
    """Writes the design tree to the file.

    Takes: the path of a run's `design-tree.json`, and the tree.
    Gives: nothing.
    Changes: writes the file as JSON, indented by one space, keys in the tree's order, closing
    with a newline, so that git shows each change by its lines.
    Refuses: CantRun where the file can't be written, naming it.
    """
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(json.dumps(tree, indent=1) + "\n")
    except OSError as error:
        raise CantRun(f"{path}: the design tree can't be written: {error}") from None


def at(tree: Tree, pointer: str) -> Any:
    """The node of the design tree at the pointer.

    Takes: the tree, and a node's JSON Pointer, such as `/deliverables/2/necessary_conditions/0`.
    Gives: the node.
    Changes: nothing.
    Refuses: Wrong where the pointer names no node of the tree, naming the pointer.
    """
    if not pointer.startswith("/"):
        raise Wrong(f"{pointer}: names no node of the design tree, as a pointer begins with /")
    node: Any = tree
    for name in pointer[1:].split("/"):
        if isinstance(node, dict) and name in node:
            node = node[name]
        elif isinstance(node, list) and name.isdecimal() and int(name) < len(node):
            node = node[int(name)]
        else:
            raise Wrong(f"{pointer}: names no node of the design tree")
    return node


def deliverable(tree: Tree, path: str) -> Deliverable:
    """The deliverable of the path.

    Takes: the tree, and a deliverable's `path`.
    Gives: the deliverable.
    Changes: nothing.
    Refuses: Wrong where no deliverable has the path, naming each path the tree holds.
    """
    for each in tree["deliverables"]:
        if each["path"] == path:
            return each
    paths = ", ".join(each["path"] for each in tree["deliverables"]) or "none"
    raise Wrong(f"{path}: no deliverable of the design tree has the path; its paths are {paths}")
