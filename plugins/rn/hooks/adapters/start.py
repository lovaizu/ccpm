#!/usr/bin/env python3
"""Lane's adapter of a start's text: `start.py <role>`, with the starts that run on its standard
input, as Lane's guide to adapters gives them. It prints the text of the start due, which points the
role to its Cut, with the Cut's path as the run value `cut`, or why no work waits for the role."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import end


def main(argv: list[str], given: str, cwd: str) -> tuple[int, str, str]:
    """Gives the start due of the role through course.due and cut.write.

    Takes: the role as the one argument, what Lane gives on standard input, and the folder of the
    run's worktree.
    Gives: 0 with `{"text": ..., "values": {"cut": ...}}`, or with `{"none": ...}` where no start
    of the role is due; 1 with what Wrong says; 2 with the usage.
    Changes: the run's folder, by the Cut written."""
    raise NotImplementedError("start.main")


if __name__ == "__main__":
    end(main(sys.argv[1:], sys.stdin.read(), os.getcwd()))
