"""wait_for: the subagent runs a command its step holds back only once its caller has approved, such
as lane:up writing the proposal into the building AI's plugin only on the building AI's OK. The lane
takes the approval, such as `OK`, then each command it holds back, such as `lay.py write`; its
sentence shows the approval alone. It is held from the subagent's record: a held command is a drift
unless a message holding the approval has reached the subagent since it last asked, by SendMessage
or by a reply that ended its turn, or since it began where it has not asked."""

from __future__ import annotations

import re

from call import Call, runs

ACTION = "wait"
WORDING = "Do not go on until `<approval>`."
TOOLS = ("Bash",)
# The sentence shows the first thing taken, the approval; the commands after it the hook alone
# holds.
SHOWN = 1


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call runs a command held back with no message holding the approval since the
    subagent last asked; never where its record is not found, as a stop then would hold even once
    the approval has come."""
    approval, held = takes[0], takes[SHOWN:]
    if call.heard is None or not runs(call, held):
        return False
    return not any(approves(m, approval) for m in call.heard)


def approves(message: str, approval: str) -> bool:
    """Whether the message holds the approval as words of their own, in any case, as `OK` in
    `OK, go on.` or `ok`, and not in `book`."""
    return re.search(rf"(?<!\w){re.escape(approval)}(?!\w)", message, re.IGNORECASE) is not None
