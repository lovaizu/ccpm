"""rn's items adapter, which Lane's guard runs at its items port for the planner's every_item lane:
given the design tree's path, its text, and the start's values on standard input, it prints the ID
of each node that the change since the run's last commit touches, as the planner answers each. A
tree not in its form, or a start that names no run, gives no item, as the planner's write of an
edit holds the tree to its form."""

from __future__ import annotations

import json
import os
import sys

ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
sys.path.insert(0, os.path.join(ROOT, "domain"))  # pragma: no mutate

import starts
import trees


def items(given: dict[str, object]) -> list[str]:
    """The IDs of the nodes the run's change touches, as the module says."""
    values = given["values"]
    run = (values.get("run") or [None])[0] if isinstance(values, dict) else None
    try:
        tree = json.loads(str(given["text"]))
        before = starts.committed_tree(run) if run else None
        if run is None or not isinstance(tree, dict):
            return []
        return trees.touched(before, tree, trees.changed(before, tree))
    except (ValueError, KeyError, TypeError):
        return []


# Run as the adapter, and not when a test imports it.
if __name__ == "__main__":  # pragma: no mutate
    print(json.dumps({"items": items(json.load(sys.stdin))}))
