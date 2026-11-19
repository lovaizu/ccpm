"""Decides which kinds a deliverable may have and which inputs it must name: a kind is a folder of
rn's best practices, `meta`, or `specific`, and a deliverable of a best practice's kind names an
input of each kind that its best practice takes."""

from __future__ import annotations

from collections.abc import Sequence

from tree.design import Tree


def faults(tree: Tree, practices: str, top: str) -> Sequence[str]:
    """Each fault of the deliverables' kinds and inputs.

    Takes: the design tree, the folder of rn's best practices, and the top of the repository, where
    an input that names no node is a file.
    Gives: one line for each deliverable whose kind is none of these, or whose inputs leave out a
    kind that its best practice's `inputs` names, with neither a node nor a file of that kind left;
    none where each holds.
    Refuses: nothing, as each fault is a line of what it gives."""
    raise NotImplementedError("inputs.faults")
