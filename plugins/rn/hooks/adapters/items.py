#!/usr/bin/env python3
"""Lane's adapter of a step's items: `items.py <role> <step>`, with the role's run values on its
standard input. It prints the ID of each practice of the best practice that the role's Cut names,
which the step carries out, or none for a step that carries out no practice."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import end


def main(argv: list[str], given: str, cwd: str, plugin: str) -> tuple[int, str, str]:
    """Gives the practices of a step.

    Takes: the role and the step's number, the run values on standard input, the folder of the
    run's worktree, and rn's folder.
    Gives: 0 with `{"items": [...]}`; 1 with what Wrong says, such as a Cut that names no best
    practice of rn's; 2 with the usage."""
    raise NotImplementedError("items.main")


if __name__ == "__main__":
    end(main(sys.argv[1:], sys.stdin.read(), os.getcwd(), os.path.join(HERE, "..", "..")))
