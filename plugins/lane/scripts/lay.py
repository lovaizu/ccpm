"""What the user runs to print the lanes and routes they propose, write them into their plugin once
approved, or bring up a plugin laid before: reads the action and its path, hands them to the
layer, its parts beside it, and prints what it gives, or what stopped it."""

from __future__ import annotations

import os
import sys

# No module before it on the path has the name of one of lane's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "hooks",
        "lane",
        "domain",
    ),
)

from layer import brought_up, printed, written
from proposal import Stop

USAGE = "usage: lay.py print <proposal>\n       lay.py write <proposal>\n       lay.py up <plugin>"
ACTIONS = {"print": printed, "write": written, "up": brought_up}


def main(argv: list[str]) -> int:
    """Prints the proposal at the path, or writes it into the plugin, or brings up the plugin at the
    path, and gives 0; prints what was wrong and gives 1."""
    if len(argv) != 2 or argv[0] not in ACTIONS:
        print(USAGE)
        return 1
    try:
        print(ACTIONS[argv[0]](argv[1]), end="")
    except Stop as stop:
        print(stop)
        return 1
    return 0


# Run as the command, and not when the tests import it under the name lay.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))
