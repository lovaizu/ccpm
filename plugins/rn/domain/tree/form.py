"""Decides how the design tree is kept as a file: read and written as JSON in the form of the
design tree best practice's `design-tree.schema.json`, each node named by its JSON Pointer, and the
tree that a run starts from, with the goal as put and the plan as its own deliverable."""

from __future__ import annotations

from typing import Any

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
    raise NotImplementedError("tree.form.started")


def read(path: str) -> Tree:
    """The design tree in the file.

    Takes: the path of a run's `design-tree.json`.
    Gives: the tree, as the file holds it, whatever its form, as `tree.checks` judges that.
    Changes: nothing.
    Refuses: Wrong where the file is missing or isn't JSON, naming it.
    """
    raise NotImplementedError("tree.form.read")


def write(path: str, tree: Tree) -> None:
    """Writes the design tree to the file.

    Takes: the path of a run's `design-tree.json`, and the tree.
    Gives: nothing.
    Changes: writes the file as JSON, indented by one space, keys in the tree's order, closing
    with a newline, so that git shows each change by its lines.
    Refuses: CantRun where the file can't be written, naming it.
    """
    raise NotImplementedError("tree.form.write")


def at(tree: Tree, pointer: str) -> Any:
    """The node of the design tree at the pointer.

    Takes: the tree, and a node's JSON Pointer, such as `/deliverables/2/necessary_conditions/0`.
    Gives: the node.
    Changes: nothing.
    Refuses: Wrong where the pointer names no node of the tree, naming the pointer.
    """
    raise NotImplementedError("tree.form.at")


def deliverable(tree: Tree, path: str) -> Deliverable:
    """The deliverable of the path.

    Takes: the tree, and a deliverable's `path`.
    Gives: the deliverable.
    Changes: nothing.
    Refuses: Wrong where no deliverable has the path, naming each path the tree holds.
    """
    raise NotImplementedError("tree.form.deliverable")
