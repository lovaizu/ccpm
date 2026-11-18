"""Decides whether each deliverable of a best practice's kind names an input for each kind that its
best practice takes: a node of the tree of that kind, or else a file outside the tree's nodes, one
for each kind left, as tree.py can tell the kind of a node alone and a deliverable built on a kind
it never read rests on a guess."""

from __future__ import annotations

import json
import os
from typing import Any

from fault import Wrong

from tree import practices
from tree.design import DesignTree, deliverables
from tree.runs import Run


def hold(run: Run, plugin_root: str, tree: DesignTree) -> None:
    """Whether each deliverable's inputs cover the kinds that its best practice takes.

    Takes: the run, rn's folder, and the tree.
    Gives: nothing, where for each deliverable not done of a best practice's kind, each kind that
    the best practice names in `inputs` is the kind of a node that its inputs name, or, for the
    kinds that no such node holds, its inputs name as many paths that no node of the tree holds.
    Changes: nothing.
    Refuses: fault.Wrong, naming each deliverable and the kinds its inputs leave out; fault.Wrong,
    as `practices.folder` does, where no best practice of a deliverable's kind exists.
    Carries: S1 `alt ... a deliverable's inputs leave out a kind that its best practice names`, and
    `T-->>K: refuses the change, naming each`.
    """
    each = deliverables(tree)
    kinds = {d["path"]: d["kind"] for d in each}
    faults = []
    for node in each:
        if node["status"] == "done" or node["kind"] == "specific":
            continue
        named = node.get("inputs", [])
        left = [k for k in _taken(run, plugin_root, node["kind"]) if k not in _kinds(named, kinds)]
        if len([p for p in named if p not in kinds]) < len(left):
            faults.append(f"{node['path']} names no input of {', '.join(left)}")
    if faults:
        raise Wrong("the design tree's inputs leave out a kind: " + "; ".join(faults))


def _taken(run: Run, plugin_root: str, kind: str) -> list[str]:
    """Each kind that the kind's best practice names in its inputs."""
    path = os.path.join(practices.folder(run, plugin_root, kind), "best-practice.json")
    with open(path, encoding="utf-8") as f:
        given: Any = json.load(f)
    return [each["kind"] for each in given.get("inputs", [])]


def _kinds(named: list[str], kinds: dict[str, str]) -> set[str]:
    """The kind of each node that the paths name."""
    return {kinds[p] for p in named if p in kinds}
