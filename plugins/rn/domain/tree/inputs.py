"""Decides which kinds a deliverable may have and which inputs it must name: a kind is a folder of
rn's best practices, `meta`, or `specific`, and a deliverable of a best practice's kind names an
input of each kind that its best practice takes."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # design.read runs this check, so the check takes only the type from it.
    from tree.design import Tree


def faults(tree: Tree, practices: str, top: str) -> Sequence[str]:
    """Each fault of the deliverables' kinds and inputs.

    Takes: the design tree, the folder of rn's best practices, and the top of the repository, where
    an input that names no node is a file.
    Gives: one line for each deliverable whose kind is none of these, or whose inputs leave out a
    kind that its best practice's `inputs` names, with neither a node nor a file of that kind left;
    none where each holds. An input counts for its node's kind, or, where it names a file of the
    repository, for the kind that the file's name gives, as `docs/test-design.md` for test-design.
    Refuses: nothing, as each fault is a line of what it gives."""
    nodes = {d["path"]: d["kind"] for d in tree["deliverables"]}
    found: list[str] = []
    for d in tree["deliverables"]:
        if d["kind"] in ("meta", "specific") or d["status"] == "done":
            continue
        practice = os.path.join(practices, d["kind"], "best-practice.json")
        if not os.path.isfile(practice):
            found.append(f"{d['path']}: its kind {d['kind']} is no best practice of rn's")
            continue
        with open(practice, encoding="utf-8") as f:
            takes = [each["kind"] for each in json.load(f).get("inputs", [])]
        kinds = {_kind(each, nodes, top) for each in d["inputs"]}
        found += [
            f"{d['path']}: its inputs name no {kind}, which the {d['kind']} best practice takes"
            for kind in takes
            if kind not in kinds
        ]
    return found


def _kind(path: str, nodes: Mapping[str, str], top: str) -> str:
    """The kind of an input: its node's, a file's that its name gives, or none."""
    if path in nodes:
        return nodes[path]
    if os.path.isfile(os.path.join(top, path)):
        return os.path.splitext(os.path.basename(path))[0].lower()
    return ""
