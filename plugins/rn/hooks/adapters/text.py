#!/usr/bin/env python3
"""Decides how the Cut of a start reaches Lane, as Lane's adapter of a start's text: the run of the
folder Lane runs it in, the Cut that tree.py's code gives there, set as one JSON line of the text,
and its run values, which the guard holds the role to."""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from typing import TextIO

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "domain"))

from tree import cut, design, runs  # noqa: F401


def main(argv: Sequence[str], stdin: TextIO, cwd: str) -> tuple[int, str, str]:
    """Gives Lane the text of one start due.

    Takes: the role, as its one argument; `{"running": [{"role", "text", "values"}]}` on standard
    input, each start that runs; and the folder the conversation works in.
    Gives, as the exit code, standard output, and standard error: 0, with `{"text": <the Cut as one
    JSON line>, "values": <its run values>}`, from `runs.of_folder`, `design.read`, and
    `cut.next_start`; 1, with why, where the folder lies in no run's worktree, as before the
    orchestrator makes and enters it, or where no work waits for the role; 2, with the usage.
    Changes: nothing.
    Refuses: as Gives says, by its exit code, which Lane reads as a failure with why.
    Carries: S1 `GD->>A: asks for the text of the tree-keeper's start`, `A-->>GD: fails, as the
    folder lies in no run's worktree yet`, `GD->>A: asks for the text of the generator's start,
    with each start that runs`, `A->>T: gets each deliverable doing, and the Cut`, and `A-->>GD:
    that start's text and run values in Lane's form`; S5 `GD->>A: asks for the text of the
    tree-keeper's start` and `A-->>GD: fails`.
    """
    raise NotImplementedError("text.main")


if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], sys.stdin, os.getcwd())
    sys.stdout.write(out)
    sys.stderr.write(err)
    raise SystemExit(code)
