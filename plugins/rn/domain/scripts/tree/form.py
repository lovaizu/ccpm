"""Decides how the design tree is kept as a file: read and written as JSON in the form of the
design tree best practice's `design-tree.schema.json`, each node named by its JSON Pointer, and the
tree that a run starts from, with its context, the goal open for the pruner to write from the
request, and the plan as its own deliverable."""

from __future__ import annotations

import json
from typing import Any

from fault import CantRun, Wrong
from practice import Practice, conditions

# A design tree, in the form of domain/best-practices/design-tree/design-tree.schema.json.
Tree = dict[str, Any]
# A deliverable of the design tree: one of `done` or `open` of its schema.
Deliverable = dict[str, Any]
# The context of a design tree: the `context` of its schema.
Context = dict[str, Any]


def context(version: str, deliverables: str, conversation: str) -> Context:
    """The context that a run starts with.

    Takes: rn's version, as its plugin.json gives it; the language of the deliverables and that of
    the conversation, each as the user settled it, such as English and Japanese.
    Gives: a context holding the version, the two languages as given, no issue to close or to
    refer to, and no pull request.
    Changes: nothing.
    Refuses: Wrong where a language is empty or only spaces, naming which.
    """
    languages = {"deliverables": deliverables, "conversation": conversation}
    for key, given in languages.items():
        if not given.strip():
            raise Wrong(
                f"the {key} language is empty; give the language of the {key} as a word, such as"
                " English"
            )
    return {
        "rn": version,
        "languages": languages,
        "issues": {"closes": [], "refs": []},
        "pr": None,
    }


def started(context: Context, plan: str, practice: Practice) -> Tree:
    """The design tree that a run starts from, before the pruner writes the goal from the request.

    Takes: the context that `context` gives; the plan's path from the run's worktree,
    `.rn/<name>/design-tree.json`, the tree's own; and the design tree best practice.
    Gives: a tree whose context is the one given; whose goal is open, `{"decided": null}`, as an
    open decision is; whose one deliverable is the plan, its name empty until the pruner names it
    by the goal, of the kind `design-tree`, at the plan's path, with no inputs, status open, and
    each necessary condition of the best practice in its order, good false, with no decision; and
    whose work and steps are none.
    Changes: nothing.
    Refuses: nothing.
    """
    held = [
        {"id": condition["id"], "good": False, "decisions": []}
        for condition in conditions(practice["goal"])
    ]
    return {
        "context": context,
        "goal": {"decided": None},
        "deliverables": [
            {
                "name": "",
                "path": plan,
                "kind": "design-tree",
                "inputs": [],
                "status": "open",
                "necessary_conditions": held,
            }
        ],
        "steps": [],
    }


def goal(tree: Tree) -> str:
    """The tree's goal, as each step that needs it takes it, such as a Cut or the pull request.

    Takes: the tree.
    Gives: the goal's `decided`.
    Changes: nothing.
    Refuses: Wrong where the goal is open, its `decided` null, saying that a new pruner writes it
    from the request first.
    """
    decided = tree["goal"]["decided"]
    if decided is None:
        raise Wrong(
            "the design tree's goal is open; hand the request to a new pruner, which writes the"
            " goal from it, and run this again once the tree holds it"
        )
    return decided


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
