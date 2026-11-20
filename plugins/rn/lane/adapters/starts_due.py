"""Decides rn's order, as Lane asks it at each move of a run: which of rn's roles start now, from
the run's design tree and its Rounds, each deliverable's Rounds beside the others', and when the
run ends."""

from __future__ import annotations

import os
import sys
from typing import Any

# rn's code lies in domain/, which comes on the import path before it's imported.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import end

# The run as Lane gives it, in the form of Lane's starts_due.in.schema.json, and the starts due
# that rn gives back, in the form of its starts_due.out.schema.json.
Given = dict[str, Any]
Due = dict[str, Any]


def due(given: Given, cwd: str) -> Due:
    """The starts due of the run, or its end.

    Takes: the run as Lane gives it, and the folder that the conversation works in, the top of the
    user's repository.
    Gives: `{"ends": true}` where the run's latest command is `rn:dn`, or each deliverable of its
    design tree is done; `{"starts": []}` where the run has no worktree yet, or its plan, the
    deliverable of the kind `design-tree`, isn't done; else `{"starts": [...]}`, for `rn:generator`
    and `rn:evaluator`, the count of each: one for each deliverable that an item `make` of `work`
    names, whose inputs are each done, that rests through its inputs on no deliverable still being
    made, and that waits on the role, as `rounds.course.next_of` gives it, a deliverable with an
    open decision waiting on the answer and on no role, less each start of the role whose prompt
    names a Cut of the deliverable and that has no result yet in the moves. The run is the one whose
    folder the latest start's prompt names, or else the first that `repository.worktree.paused`
    gives.
    Changes: nothing.
    Refuses: Wrong where the design tree or a Round can't be read, naming the file.
    """
    raise NotImplementedError("starts_due.due")


def main(stdin: str, cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of the adapter, as Lane runs it.

    Takes: what Lane writes on its standard input, and the folder it runs in.
    Gives: 0 with `due`'s output as one line of JSON; 1 with `starts_due.py: <what's wrong>`
    where the input isn't JSON or `due` refuses it as Wrong; 2 with what stopped it where it
    CantRun. Lane stops the move at hand on any but 0.
    Changes: nothing.
    Refuses: nothing; each fault is its exit code.
    """
    raise NotImplementedError("starts_due.main")


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd()))
