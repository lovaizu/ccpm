"""The E2E test of a stopped run going on, as pin's README promises, "a stopped run goes on from
there in a new conversation", and its architecture's story "go on with a stopped run in a new
conversation, from the tree it kept": in the notes app's repository, the person starts
`/pin:down` with the plan, answers three messages and leaves; in a new conversation, they give
`/pin:down` the same plan again. The person is stood in for by an AI that answers from the intent
and remembers the first conversation.

Breaks it invites: starting a second tree for the same plan, and asking again what the person
answered in the first conversation. A run counts only where the tree held, when the person left, a
decision the person had settled.

Each run passes where: .pin/ holds one tree; each decision the person had settled when they left is
decided the same at the end; no message of the second conversation asked again what was settled;
and the second conversation passes as trial_down.py's runs do. Run as
`python3 dev/pin/tests/e2e/trial_resume.py [runs] [first]`."""

from __future__ import annotations

import os
import time

import pinning
from pinning import trying

FIRST = "/pin:down notes list should give JSON as well, so my scripts stop parsing its text"
# The answers the person gives before they leave: the goal, and two points after it.
LEFT_AFTER = 3


def run(number: int) -> bool:
    """One run of the E2E test; prints what it found, and gives whether it passed and counted."""
    place = trying.folder("pin", f"trial-resume-{number}")
    repo, copies = pinning.made(place, {})
    started = time.monotonic()
    first = trying.Conversation([copies["pin"]], repo, wait=8)
    try:
        before = pinning.talked(
            first, FIRST, place, os.path.join(place, "first.jsonl"), stop_after=LEFT_AFTER
        )
    finally:
        first.close()
    print("  the person left; a new conversation starts")
    found = pinning.pinned(repo)
    if not found:
        return False
    _, kept = found
    theirs = {d["id"]: d["decided"] for d in kept["decisions"] if d["settled_by"] == "user"}
    second = trying.Conversation([copies["pin"]], repo, wait=8)
    try:
        stream = os.path.join(place, "stream.jsonl")
        turns = pinning.talked(second, FIRST, place, stream, before=before)
    finally:
        second.close()
    print(f"  {len(before)} + {len(turns)} messages, {time.monotonic() - started:.0f} s")
    found = pinning.pinned(repo)
    if not found:
        return False
    path, tree = found
    untried = [] if theirs else ["the person had settled no decision when they left"]
    decided = {d["id"]: d["decided"] for d in tree["decisions"]}
    wrong = [f"{i} changed from {d!r}" for i, d in theirs.items() if decided.get(i) != d]
    wrong += pinning.judged(copies["pin"], path, place, turns)
    return pinning.verdict(untried, wrong)


if __name__ == "__main__":
    pinning.main(run)
