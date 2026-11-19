#!/usr/bin/env python3
"""Decides which practices make a step's checklist: the generator's step that decides holds each
decide item of its Cut's best practice, its step that makes each make item, in the best practice's
order, an evaluator's step that judges each condition of its Cut, and any other step none."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import end


def main(given: str, cwd: str, plugin: str) -> tuple[int, str, str]:
    """Gives Lane the items of a step's checklist, as Lane runs this adapter for a step whose rule
    asks for a checklist.

    Takes: the run, the role, and the step, on standard input in the form of Lane's
    checklist.in.schema.json; the folder of the run's worktree; and rn's folder.
    Gives: 0 with `{"items": [...]}`, in the form of Lane's checklist.out.schema.json: for
    `rn:generator`'s step 2 each `N<n>.<m>` of its Cut's best practice that its maker takes while
    deciding, the m-th practice of the condition N<n>, and for its step 3 each that it takes while
    making; for `rn:evaluator`'s step 3 the ID of each condition of its Cut; and none for any other
    step. 1 with what Wrong says, such as Lane's input out of its form, or a Cut that names no best
    practice of rn's.
    Changes: nothing.
    Refuses: nothing beyond the exit codes above. Which Cut the step's start holds, Lane's input
    doesn't name, as dev/rn/skeleton-gaps.md says."""
    raise NotImplementedError("checklist.main")


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd(), os.path.join(HERE, "..", "..")))
