#!/usr/bin/env python3
"""Decides which run's results Lane picks up, as Lane's adapter of the plugin's records: none where
words follow /rn:up, as they're a request; else the run of the worktree that holds the folder, or
the one run left; and each result that rn's check kept in its records."""

from __future__ import annotations

import json
import os
import sys
from typing import TextIO

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "domain"))

from fault import CantRun, Missing, Wrong
from record import form
from tree import records, runs


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
    try:
        given = json.loads(stdin.read())
        words = given["words"] if isinstance(given, dict) else None
        if not isinstance(words, str):
            raise Wrong('standard input must be {"words": <the words typed after /rn:up>}')
        found = [] if words.strip() else _kept(cwd)
    except ValueError:
        return 1, "", "rn's adapter of the records: standard input isn't JSON\n"
    except (KeyError, Wrong, Missing, CantRun) as e:
        return 1, "", f"rn's adapter of the records: {e}\n"
    return 0, json.dumps({"results": found}) + "\n", ""


def _kept(cwd: str) -> list[dict[str, str]]:
    """Each result kept in the records of the run of the folder, or of the one run left."""
    run = runs.of_folder(cwd)
    if run is None:
        left = runs.left(cwd)
        run = left[0] if len(left) == 1 else None
    if run is None:
        return []
    held = [form.read(os.path.join(run.worktree, each)).kept for each in records.in_order(run)]
    return [{"role": k.role, "result": k.result} for k in held if k]


if __name__ == "__main__":
    code, out, err = main(sys.stdin, os.getcwd())
    sys.stdout.write(out)
    sys.stderr.write(err)
    raise SystemExit(code)
