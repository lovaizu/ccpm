"""The E2E test of O1 of pin's UX, "The person pins down the plan with /pin:down", as the README's
walkthrough runs it: in the notes app's repository, Claude Code on Opus, with a copy of pin, is
given `/pin:down` with the plan, and the person is stood in for by an AI that answers from an
intent written beforehand and never shown pin.

Breaks it invites: asking the person a fact the repository holds, as which scripts read the output
and how sync.py reads `updated`; asking several decisions at once, as more than one is open from
the start; and settling for the person what is theirs, as the form of the JSON and of tags. A run
counts only where a decision rests on a fact quoted from scripts/, and check.py once named more
than one decision open at once.

Each run passes where: the tree at `.pin/<yyyymmdd>-<name>/design-tree.json` passes check.py with
no decision open; each message to the person held one point, asked no fact of the repository and
asked nothing again; the design was shown to the person to confirm; and the tree holds each point
of the intent, the person's own settled by them. Run as `python3 dev/pin/tests/ux/trial_down.py
[runs] [first]`; it prints the folder of each run, where the run's stream is kept."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))

import pinning
from pinning import trying

FIRST = "/pin:down notes list should give JSON as well, so my scripts stop parsing its text"


def run(number: int) -> bool:
    """One run of the E2E test; prints what it found, and gives whether it passed and counted."""
    place = trying.folder("pin", f"trial-down-{number}")
    repo, copies = pinning.made(place, {})
    stream = os.path.join(place, "stream.jsonl")
    turns = pinning.conversed([copies["pin"]], repo, FIRST, place, stream)
    found = pinning.tree_and_untried(repo, stream)
    if not found:
        return False
    path, _, untried = found
    return pinning.verdict(untried, pinning.judged(copies["pin"], path, place, turns))


if __name__ == "__main__":
    pinning.main(run)
