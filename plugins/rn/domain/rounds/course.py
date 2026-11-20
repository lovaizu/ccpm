"""Decides which Round a deliverable takes next: content made until each condition is good, then
refactored until each is good again, each stage at most LIMIT Rounds, none while a point waits on
the user, and after them none, each finding left kept by the orchestrator as an open decision."""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple, Optional

from tree.form import Deliverable

from rounds.files import Result, Round

# The most Rounds of content, and of refactoring, that a deliverable takes, as remaking has a
# limit (the architecture's P3.3).
LIMIT = 2

# A Round so far, with the generator's result and the evaluator's in it, None where the role
# wrote none yet.
Done = tuple[Round, Optional[Result], Optional[Result]]


class Next(NamedTuple):
    """What a deliverable waits on, with the stage, `content` or `refactor`, of the Round where a
    role is to start: `generator`, in a new Round or, where `resumes`, the last Round again;
    `evaluator`, in the last Round; `answer`, the user's answer to an open decision;
    `orchestrator`, to keep each finding left past the limit as an open decision; or `sign-off`."""

    waits_on: str
    stage: str | None
    resumes: bool


def next_of(deliverable: Deliverable, rounds: Sequence[Done], refactors: bool) -> Next:
    """What the deliverable waits on, from its node of the design tree and its Rounds so far.

    Takes: the deliverable's open node, each of its Rounds in order with their results, and
    whether its kind is refactored, as `practice.refactoring` gives a kind.
    Gives, the first that holds:
    - the answer, where a decision of the node is open, its `decided` null;
    - the generator resuming the last Round, where the last generator's result is `point`, as
      the decision that held its point is answered now;
    - the evaluator in the last Round, where the last generator's result is `made` and the
      evaluator's is missing;
    - the generator in a new content Round, where there's no Round yet;
    - where a condition of the node isn't good: the generator in a new Round of the last Round's
      stage, where that stage has fewer than LIMIT Rounds, else the orchestrator;
    - where each condition is good: the generator in a new refactor Round, where the kind is
      refactored and it has no refactor Round yet; else the sign-off.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("rounds.course.next_of")
