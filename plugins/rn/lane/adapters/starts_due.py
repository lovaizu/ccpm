#!/usr/bin/env python3
"""Decides what rn's order gives Lane at each move: the starts due of the run, from its design tree
and its Rounds as course.due gives them, or the run's end."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import end


def main(given: str, cwd: str) -> tuple[int, str, str]:
    """Gives Lane the starts due of the run, as Lane runs this adapter at each move.

    Takes: the run as Lane's order sees it, on standard input in the form of Lane's
    starts_due.in.schema.json, and the folder that the conversation works in: the repository's top,
    or rn's worktree of the run.
    Gives: 0 with, in the form of Lane's starts_due.out.schema.json:
    - `{"ends": true}` where the run's latest command is /rn:ty and no run's folder that
      rounds.folder finds has work left, as that /rn:ty signs off the pull request;
    - else `{"starts": [...]}`, for each role, `rn:generator` or `rn:evaluator`, the starts that
      course.due gives for the design tree of the run's folder that rounds.folder finds and that
      folder's Rounds, less each start of the role in the run's moves that has no result after it,
      as it still runs: one generator for each deliverable whose inputs are done and that rests on
      none still being made, beside the others, or one evaluator for each group of conditions that
      its Round judges. Each start of a Round with its Cut and no result, as one stopped, counts as
      due, so that a pick-up in a new conversation, whose moves hold no start yet, starts each role
      stopped again from the run's own files. None where the words ask for a new run and the moves
      hold no /rn:ty yet, as the plan waits for the person's sign-off, or where no run's folder has
      work left.
    1 with what Wrong says, such as Lane's input out of its form, or a design tree or a Round that
    isn't JSON.
    Changes: nothing.
    Refuses: nothing beyond the exit codes above."""
    raise NotImplementedError("starts_due.main")


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd()))
