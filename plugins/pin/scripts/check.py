"""What a pinner runs, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py <design tree>`, to learn
whether the design tree holds: reads the path, hands the tree to tree.py in core/domain/, and
prints that it holds with the decisions open to decide now, giving 0; each problem, giving 1; or
why it could not check, giving 2."""

from __future__ import annotations

import os
import sys

# No module before it on the path has the name of pin's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain"),
)

from tree import Unreadable, load, problems, ready

USAGE = "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py <design tree>"
HOLDS = (
    "every question is served, every decision reaches the goal, and each decision comes after the"
    " ones it builds on."
)


def main(argv: list[str]) -> int:
    """Checks the design tree at the one path given, prints what it found, and gives 0 where the
    tree holds, 1 where it does not, and 2 where it could not check it or was not given one path."""
    try:
        (path,) = argv
    except ValueError:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        tree = load(path)
    except Unreadable as why:
        lines = "".join(f"- {line}\n" for line in str(why).splitlines())
        print(f"check.py: could not check {path}:\n{lines}", end="", file=sys.stderr)
        return 2
    found = problems(tree)
    if found:
        print(f"check.py: {path} does not hold:")
        for problem in found:
            print(f"- {problem}")
        return 1
    print(f"check.py: {path} holds: {HOLDS}")
    open_now = ready(tree)
    print(f"Open to decide now: {', '.join(open_now)}." if open_now else "No decision is open.")
    return 0


# Run as the command, and not when the tests import it under the name check.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))
