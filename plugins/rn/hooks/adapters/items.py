#!/usr/bin/env python3
"""Lane's adapter of a step's items: `items.py <role> <step>`, with the role's run values on its
standard input. It prints the ID of each practice of the best practice that the role's Cut names, in
the best practice's order, as Lane asks only of a step that carries out a best practice's
practices."""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import Wrong, end
from schemas import form

USAGE = "usage: items.py <role> <step>, with the role's run values on standard input\n"


def main(argv: list[str], given: str, cwd: str, plugin: str) -> tuple[int, str, str]:
    """Gives the practices of a step.

    Takes: the role and the step's number, the run values on standard input, the folder of the
    run's worktree, and rn's folder.
    Gives: 0 with `{"items": [...]}`, each `N<n>.<m>`, the m-th practice of the condition N<n>; 1
    with what Wrong says, such as a Cut that names no best practice of rn's, or where Lane's input
    names no Cut; 2 with the usage."""
    if len(argv) != 2:
        return 2, "", USAGE
    try:
        cut = json.loads(given)["values"]["cut"]
    except (ValueError, KeyError, TypeError):
        return 1, "", 'items.py: Lane\'s input isn\'t {"values": {"cut": ...}}\n'
    try:
        schema = os.path.join(plugin, "domain", "schemas", "cut.schema.json")
        practice = form.read(os.path.join(cwd, cut), schema, cut)["best_practice"]
        return 0, json.dumps({"items": _practices(plugin, practice)}), ""
    except Wrong as wrong:
        return 1, "", f"items.py: {wrong}\n"


def _practices(plugin: str, practice: str) -> list[str]:
    """The ID of each practice of the best practice, in its order; Wrong, naming it, where rn has no
    such best practice."""
    path = os.path.join(plugin, "domain", "best-practices", practice, "best-practice.json")
    if not os.path.isfile(path):
        raise Wrong(f"rn has no best practice {practice}, which the Cut names")
    with open(path, encoding="utf-8") as f:
        factors = json.load(f)["goal"]["critical_success_factors"]
    return [
        f"{n['id']}.{i}"
        for c in factors
        for n in c["necessary_conditions"]
        for i in range(1, len(n["items"]) + 1)
    ]


if __name__ == "__main__":
    end(main(sys.argv[1:], sys.stdin.read(), os.getcwd(), os.path.join(HERE, "..", "..")))
