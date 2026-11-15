#!/usr/bin/env python3
"""Decides which run's results Lane picks up, as Lane's adapter of the plugin's records: none where
words follow /rn:up, as they're a request; else the run of the worktree that holds the folder, or
the one run left; and each result that rn's check kept in its records."""

from __future__ import annotations

import os
import sys
from typing import TextIO

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "domain"))

from record import form  # noqa: F401
from tree import records, runs  # noqa: F401


def main(stdin: TextIO, cwd: str) -> tuple[int, str, str]:
    """Gives Lane the results kept of the run to pick up.

    Takes: `{"words": <the words typed after /rn:up>}` on standard input, and the folder the
    conversation works in.
    Gives, as the exit code, standard output, and standard error: 0, with `{"results": [{"role",
    "result"}]}` in the order of the starts, from `runs.of_folder` or `runs.left`,
    `records.in_order`, and `form.read`, or with no results where words follow /rn:up, or where no
    run or more than one is left; 1, with why, where standard input or a record leaves its form.
    Changes: nothing.
    Refuses: as Gives says, by its exit code, which Lane reads as a failure with why.
    Carries: S1 `GD->>A: asks for the results kept, as /rn:up loads, with the words typed after it`
    and `A-->>GD: none`; S5 `GD->>A: asks for the results kept`, `A->>T: gets the run of the
    worktree that holds the folder, or else the runs left, and each Record of the run in the order
    of its starts`, `A->>R: gets the result kept in each of those records`, and `A-->>GD: those
    results in Lane's form` or `none`.
    """
    raise NotImplementedError("records.main")


if __name__ == "__main__":
    code, out, err = main(sys.stdin, os.getcwd())
    sys.stdout.write(out)
    sys.stderr.write(err)
    raise SystemExit(code)
