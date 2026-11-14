"""Decides, for Lane's own up, whether up gave the person what `lay.py print` showed, word for
word, whether a run of `lay.py write` is the caller's own act, and when a Run of up ends without
one, as the principle Laid only on the caller's own act says."""

from __future__ import annotations

from domain.event import Call
from domain.run_record import Run


def shown_whole(run: Run, message: str) -> bool:
    """Whether the message that ends up's turn holds what `lay.py print` showed last, word for
    word; true where no `lay.py print` showed anything in the Run."""
    raise NotImplementedError("approval.shown_whole")


def own_act(run: Run, call: Call) -> bool:
    """Whether the call, a run of `lay.py write`, is its caller's own act: in a Run that a person's
    typed `/lane:up` started, the person typed a prompt since the last `lay.py print`; in a Run
    that an AI's call of the skill started, its own run of the command is the act. A call that
    isn't a run of `lay.py write` is no act."""
    raise NotImplementedError("approval.own_act")


def ends_unapproved(run: Run) -> bool:
    """Whether the Run of up ends as its turn ends: a person typed a prompt after a Proposal shown,
    and the turn made no `lay.py write` and no new `lay.py print`, as a Proposal waits for one
    reply."""
    raise NotImplementedError("approval.ends_unapproved")
