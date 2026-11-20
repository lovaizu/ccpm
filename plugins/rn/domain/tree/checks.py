"""Decides which faults keep a change of the design tree from its commit: the tree's schema, and
each condition of the design tree best practice that code can check."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from check.form import faults as form_faults
from practice import Practice

from tree.form import Deliverable, Tree

# The design tree's schema, beside its best practice in rn's folder.
_SCHEMA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "best-practices",
    "design-tree",
    "design-tree.schema.json",
)
# The statuses of a deliverable not yet done.
_OPEN = ("open", "doing")


def faults(tree: Tree, practices: Mapping[str, Practice], worktree: str) -> list[str]:
    """Each fault of the design tree, in a line that says where and how to mend it.

    Takes: the tree, the best practice of each kind by its name, as `practice.kinds` finds them,
    and the run's worktree.
    Gives: each place, by its JSON Pointer, where the tree leaves its schema; where a deliverable's
    kind is no kind of `practices`; where an open deliverable's necessary conditions aren't its
    best practice's, in their order; where an input names neither a deliverable's path nor a file
    of the worktree; where a deliverable rests on itself through its inputs; and where an item of
    `work` names no deliverable, or a `decide` names no condition or `about` of it. None where the
    tree holds each.
    Changes: nothing.
    Refuses: nothing.
    """
    found = form_faults(tree, _SCHEMA)
    if found:
        # The checks below read the tree in its form, so a tree out of it gets its form's faults.
        return found
    deliverables = tree["deliverables"]
    paths = {each["path"]: each for each in deliverables}
    for index, node in enumerate(deliverables):
        at = f"/deliverables/{index}"
        found += _kind(node, practices, at)
        found += [
            f"{at}/inputs/{place}: names {each}, which is neither a deliverable's path nor a file"
            " of the run's worktree; name one of them"
            for place, each in enumerate(node.get("inputs", []))
            if each not in paths and not os.path.isfile(os.path.join(worktree, each))
        ]
        if _rests_on(node["path"], node, paths, set()):
            found.append(f"{at}: rests on itself through its inputs; take its own path out of them")
    found += [
        fault for place, item in enumerate(tree["work"]) for fault in _work(item, paths, place)
    ]
    return found


def _kind(node: Deliverable, practices: Mapping[str, Practice], at: str) -> list[str]:
    """The faults of the deliverable's kind, and of an open one's conditions against it."""
    if node["kind"] not in practices:
        kinds = ", ".join(sorted(practices))
        return [f"{at}/kind: takes one of the kinds of the best practices, {kinds}"]
    if node["status"] not in _OPEN:
        return []
    practice = practices[node["kind"]]
    wanted = [
        condition["id"]
        for factor in practice["goal"]["critical_success_factors"]
        for condition in factor["necessary_conditions"]
    ]
    held = [each["id"] for each in node["necessary_conditions"]]
    if held == wanted:
        return []
    return [
        (
            f"{at}/necessary_conditions: holds {', '.join(held) or 'none'}; its kind"
            f" {node['kind']} takes {', '.join(wanted)}, in that order"
        )
    ]


def _rests_on(
    path: str, node: Deliverable, paths: Mapping[str, Deliverable], seen: set[str]
) -> bool:
    """Whether the deliverable rests on the path through its inputs, each deliverable seen once."""
    for each in node.get("inputs", []):
        if each == path:
            return True
        if each in paths and each not in seen:
            seen.add(each)
            if _rests_on(path, paths[each], paths, seen):
                return True
    return False


def _work(item: dict[str, Any], paths: Mapping[str, Deliverable], place: int) -> list[str]:
    """The fault of the item of the work, where it names no deliverable, or no point of it."""
    at = f"/work/{place}"
    if item["path"] not in paths:
        return [f"{at}: names {item['path']}, which no deliverable has; name a deliverable's path"]
    if item["do"] != "decide":
        return []
    conditions = {each["id"]: each for each in paths[item["path"]].get("necessary_conditions", [])}
    condition = conditions.get(item.get("condition", ""))
    if condition is None:
        return [f"{at}: names no condition of {item['path']}; name one of {', '.join(conditions)}"]
    abouts = [each["about"] for each in condition["decisions"]]
    if item.get("about") in abouts:
        return []
    return [
        (
            f"{at}: names no point of {item['path']}'s {condition['id']}; name the about of one of"
            f" its decisions, {', '.join(abouts) or 'none yet'}"
        )
    ]
