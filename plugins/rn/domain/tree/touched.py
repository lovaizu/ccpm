"""Decides which nodes of the design tree a change touches: the nodes that differ from the tree as
last committed, and those that the links between the nodes reach from each, as the design tree
best practice's N4 lists them."""

from __future__ import annotations

from typing import Any

from tree.form import Tree, at

# The order of the tree's parts, from the goal down.
_PARTS = {"goal": 0, "deliverables": 1, "work": 2}
# The depth, in a pointer's names, of each node of a deliverable: the deliverable, a condition, and
# a decision.
_DELIVERABLE, _CONDITION, _DECISION = 2, 4, 6


def touched(before: Tree, after: Tree, pointer: str) -> list[str]:
    """The nodes that a change to the node touches, to read again beside the change.

    Takes: the tree as last committed, the tree as it stands, and the changed node's JSON Pointer
    in the tree as it stands.
    Gives: the JSON Pointer in the tree as it stands of each node up to the goal; of each later
    decision of the same deliverable; of each deliverable whose inputs name the changed
    deliverable's path, the old one or the new one, or that it names there; and of each item of
    `work` that names either path; each once, from the goal down, the changed node left out.
    Changes: nothing.
    Refuses: Wrong where the pointer names no node, as `tree.form.at` refuses.
    """
    at(after, pointer)
    names = pointer[1:].split("/")
    found = {"/goal"}
    depths = {"work": (2,), "deliverables": (_DELIVERABLE, _CONDITION, _DECISION)}
    found |= {_pointer(names[:depth]) for depth in depths.get(names[0], ()) if depth <= len(names)}
    if names[0] == "deliverables" and len(names) >= _DELIVERABLE:
        found |= _linked(before, after, int(names[1]))
        if len(names) >= _DECISION:
            found |= _later(after, int(names[1]), int(names[3]), int(names[5]))
    found.discard(pointer)
    return sorted(found, key=_order)


def changed(before: Tree, after: Tree) -> list[str]:
    """The nodes that a change made.

    Takes: the tree as last committed, and the tree as it stands.
    Gives: the JSON Pointer of each deepest node whose value differs, or that one of them holds
    and the other doesn't, from the goal down; none where they're equal.
    Changes: nothing.
    Refuses: nothing.
    """
    return _differ(before, after, "")


def _linked(before: Tree, after: Tree, index: int) -> set[str]:
    """The deliverables and items of the work that the links reach from the deliverable."""
    node = after["deliverables"][index]
    paths = {node["path"]}
    if index < len(before["deliverables"]):
        paths.add(before["deliverables"][index]["path"])
    found = set()
    for other, each in enumerate(after["deliverables"]):
        names_it = paths & set(each.get("inputs", []))
        if other != index and (names_it or each["path"] in node.get("inputs", [])):
            found.add(f"/deliverables/{other}")
    found |= {f"/work/{place}" for place, item in enumerate(after["work"]) if item["path"] in paths}
    return found


def _later(after: Tree, index: int, condition: int, decision: int) -> set[str]:
    """Each decision of the deliverable after the one at the condition and the decision."""
    conditions = after["deliverables"][index]["necessary_conditions"]
    return {
        f"/deliverables/{index}/necessary_conditions/{c}/decisions/{d}"
        for c, each in enumerate(conditions)
        for d in range(len(each["decisions"]))
        if (c, d) > (condition, decision)
    }


def _differ(before: Any, after: Any, pointer: str) -> list[str]:
    """The pointer of each deepest node under the pointer where the two values differ."""
    if isinstance(before, dict) and isinstance(after, dict):
        keys = list(after) + [key for key in before if key not in after]
        return [found for key in keys for found in _either(before, after, key, f"{pointer}/{key}")]
    if isinstance(before, list) and isinstance(after, list):
        return [
            found
            for index in range(max(len(before), len(after)))
            for found in _either(
                dict(enumerate(before)), dict(enumerate(after)), index, f"{pointer}/{index}"
            )
        ]
    return [] if before == after else [pointer]


def _either(before: dict[Any, Any], after: dict[Any, Any], key: Any, pointer: str) -> list[str]:
    """The changes at the key of two nodes: the key's own pointer where one of them lacks it."""
    if key in before and key in after:
        return _differ(before[key], after[key], pointer)
    return [pointer]


def _pointer(names: list[str]) -> str:
    """The JSON Pointer of the names."""
    return "/" + "/".join(names)


def _order(pointer: str) -> tuple[Any, ...]:
    """Where the node lies in the tree, from the goal down, as a key to sort by."""
    names = pointer[1:].split("/")
    return (_PARTS[names[0]], *(int(name) if name.isdecimal() else name for name in names[1:]))
