"""What the building AI runs to have the layer print the lanes it proposes, write them into its
plugin once approved, or bring up a plugin laid before: reads the action and its path, hands them to
the layer and prints what it gives, or what stopped it."""

from __future__ import annotations

import sys

import placed

# The lanes, the hooks' form and the reading of a step are lane's code's, which the guard reads them
# by too.
sys.path.insert(0, placed.CODE)

from layer import brought_up, printed, written
from proposal import Stop

USAGE = "usage: lay.py print <proposal>\n       lay.py write <proposal>\n       lay.py up <plugin>"


def main(argv: list[str]) -> int:
    """Prints the proposal at the path, or writes it into the plugin, or brings up the plugin at the
    path, and gives 0; prints what was wrong and gives 1."""
    actions = {"print": printed, "write": written, "up": brought_up}
    if len(argv) != 2 or argv[0] not in actions:
        print(USAGE)
        return 1
    try:
        print(actions[argv[0]](argv[1]), end="")
    except Stop as stop:
        print(stop)
        return 1
    return 0


# Run as the command, and not when the tests import it under the name lay.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))
