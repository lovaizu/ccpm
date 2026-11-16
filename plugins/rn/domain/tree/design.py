"""Decides the design tree's form on disk, `design-tree.json` in a run's folder, as the design tree
best practice's `design-tree.schema.json` gives it: how tree.py reads it, applies a change to its
nodes by their paths, writes it, and tells what changed."""

from __future__ import annotations

import copy
import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

import json_form
from fault import CantRun, Wrong

from tree.runs import Run

# The form of a design tree, which the design tree best practice gives.
_FORM = os.path.join("best-practices", "design-tree", "design-tree.schema.json")
# The fields of a node that hold the nodes under it, each a list: a deliverable under the top, a
# necessary condition under a deliverable, and a decision under a necessary condition or under a
# deliverable of its own kind.
_UNDER = ("deliverables", "necessary_conditions", "decisions")


@dataclass(frozen=True)
class DesignTree:
    """A run's design tree: the goal, its decisions, and the plan of deliverables, as JSON in the
    design tree best practice's form."""

    data: Mapping[str, object]


@dataclass(frozen=True)
class Change:
    """What the tree-keeper writes into the tree: each node, by its path such as
    `deliverables/3/necessary_conditions/0/decisions/1`, with its new content, or None to remove
    it, such as the goal drafted, a Decision, or a Deliverable marked done once it's signed off."""

    nodes: Mapping[str, object]


def read(run: Run) -> DesignTree:
    """The run's design tree.

    Takes: the run.
    Gives: the tree in its folder.
    Changes: nothing.
    Refuses: fault.Wrong, naming each place out of form, where the file leaves the schema;
    fault.CantRun, where it can't be read or isn't JSON.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut`, `O->>T: gets the round`, and each
    `K->>T: writes`, which read the tree first.
    """
    path = _path(run)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise CantRun(f"the design tree {path} can't be read: {e}") from None
    json_form.hold(data, json_form.load(_FORM), "design-tree.json")
    return DesignTree(data)


def apply(tree: DesignTree, change: Change) -> DesignTree:
    """The tree with a change made to its nodes.

    Takes: the tree, and the change.
    Gives: the tree changed.
    Changes: nothing.
    Refuses: fault.Wrong, naming each place, where a path names no node or the tree changed leaves
    the schema.
    Carries: S1 `K->>T: writes them, and commits (Design tree)`, and `K->>T: writes the decision`;
    S2 and S3 `K->>T: writes it`.
    """
    data = copy.deepcopy(dict(tree.data))
    for path, node in change.nodes.items():
        _set(data, path, node)
    json_form.hold(data, json_form.load(_FORM), "the change to the design tree")
    return DesignTree(data)


def changed(before: DesignTree, after: DesignTree) -> tuple[str, ...]:
    """The path of each node that differs between two trees.

    Takes: the tree before and after a change.
    Gives: each path, in the order of the tree.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `T-->>K: what changed, and each node they touch`.
    """
    return tuple(_differ("", dict(before.data), dict(after.data)))


def write(run: Run, tree: DesignTree) -> str:
    """Writes the run's design tree.

    Takes: the run, and the tree.
    Gives: the path written, from the worktree.
    Changes: the run's design-tree.json.
    Refuses: nothing; the run's folder is rn's own, so a fault in writing it stops with its trace.
    Carries: S1 `K->>T: writes them, and commits (Design tree)`.
    """
    path = _path(run)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree.data, f, indent=2)
        f.write("\n")
    return os.path.relpath(path, run.worktree)


def nodes(tree: DesignTree) -> tuple[str, ...]:
    """The path of each node of the tree, in the order of the tree.

    Takes: the tree.
    Gives: the goal's path, `goal`, where the tree holds one, then each deliverable's, each followed
    by the paths of the nodes under it.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `T-->>K: what changed, and each node they touch`, given in the order of the tree.
    """
    data = dict(tree.data)
    return (("goal",) if "goal" in data else ()) + tuple(_under("", data))


def deliverables(tree: DesignTree) -> list[Any]:
    """Each deliverable of the tree.

    Takes: the tree.
    Gives: each deliverable as the tree holds it, in the order of the work; none in a tree that no
    change has written yet.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut`, and each module of tree.py that
    reads the plan.
    """
    return list(cast(Any, tree.data).get("deliverables", []))


def goal(tree: DesignTree) -> str:
    """The tree's goal, as it was decided.

    Takes: a tree that a change has written.
    Gives: the goal's `decided`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: ... the Cut`, which names the goal; S3 `T->>RP: pushes, and opens or keeps
    the draft pull request`, which takes it as its title.
    """
    return cast(Any, tree.data)["goal"]["decided"]


def _path(run: Run) -> str:
    return os.path.join(run.folder, "design-tree.json")


def _under(path: str, node: Mapping[str, Any]) -> list[str]:
    """The path of each node under the node, in the order of the tree."""
    found = []
    for field in _UNDER:
        for number, each in enumerate(node.get(field, [])):
            at = f"{path}/{field}/{number}".lstrip("/")
            found += [at, *_under(at, each)]
    return found


def _set(data: dict[str, Any], path: str, node: object) -> None:
    """Sets the node at the path in the data, appends it one past the end of a list, or removes it
    where it's None; raises Wrong where the path names no node."""
    *above, last = path.split("/")
    held: Any = data
    try:
        for part in above:
            held = held[int(part)] if isinstance(held, list) else held[part]
        if isinstance(held, list):
            _set_item(held, int(last), node)
        # Runs only where a change takes a field out of a node, which no case reaches, as a
        # deliverable marked done is written whole; taken back to the cases' designer.
        elif node is None:  # pragma: no cover
            del held[last]
        elif isinstance(held, dict) and (last in held or not above):
            held[last] = node
        else:
            raise KeyError(last)
    except (KeyError, IndexError, ValueError, TypeError):
        raise Wrong(f"the change's path {path} names no node of the design tree") from None
    if not above and last not in ("goal", "deliverables"):
        raise Wrong(f"the change's path {path} names no node of the design tree")


def _set_item(held: list[Any], number: int, node: object) -> None:
    if node is None:
        del held[number]
    elif number == len(held):
        held.append(node)
    else:
        held[number] = node


def _differ(path: str, before: Mapping[str, Any], after: Mapping[str, Any]) -> list[str]:
    """The path of each node that differs between two nodes of one path, a node added or removed
    given once, and a node whose own fields differ given before the nodes under it that differ."""
    found = []
    if path == "" and before.get("goal") != after.get("goal"):
        found.append("goal")
    own = [k for k in {**before, **after} if k not in _UNDER and (path or k != "goal")]
    if path and any(before.get(k) != after.get(k) for k in own):
        found.append(path)
    for field in _UNDER:
        old, new = before.get(field, []), after.get(field, [])
        for number in range(max(len(old), len(new))):
            at = f"{path}/{field}/{number}".lstrip("/")
            if number >= len(old) or number >= len(new):
                found.append(at)
            else:
                found += _differ(at, old[number], new[number])
    return found
