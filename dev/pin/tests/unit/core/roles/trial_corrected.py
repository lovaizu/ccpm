"""The unit trial of a fact the person corrects, the branch of pin's architecture's first sequence
"the person corrects it": the correction is written into the decision's grounds, and the decision
is written in its turn "by the person where their correction changed it".
The repository is trial_pinner.py's, its tools beside the app, so the fact is one a search finds;
the researcher, stood in for as in trial_pinner.py, gives one fact more, that the notes' `updated`
is in UTC, which the person knows to be wrong: each note keeps the offset of where it was written.
The person is stood in for by an AI that answers from an intent never shown pin, and corrects the
fact when it is shown to them.

Breaks it invites: keeping the fact as found and deciding the form of updated as UTC; settling that
decision by research or by reasoning once the person's correction has changed it; and asking the
person to confirm the fact again after they corrected it. A run counts only where a message showed
the person the fact that updated is in UTC.

Each run passes where: the tree gives updated with each note's own offset, decided by the person;
and the run passes as trial_pinner.py's do, but for the JSON's shape. Run as
`python3 dev/pin/tests/unit/core/roles/trial_corrected.py [runs] [first]`."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..")))

import pinning
import trial_pinner

# The fact the researcher gives that the person corrects: sync.py drops the offset, which a search
# reads as updated being in UTC.
FOUND = (
    "The notes' updated is in UTC: sync.py drops its offset and compares it with LAST, of no zone:",
    "- " + pinning.line_of("scripts/sync.py", "fromisoformat"),
    "- " + pinning.line_of("scripts/sync.py", "LAST = "),
)
INTENT = trial_pinner.INTENT + (
    "\n\nOne fact you know better than the repository shows. Where you are shown that updated is"
    " in UTC, or is taken as UTC, say it is not right: updated is the local time each note was"
    " written in, with its offset, such as +09:00 for a note you wrote in Tokyo; the two notes"
    " here are in UTC only by chance, and sync.py dropping the offset is a fault of its own. The"
    " JSON keeps each note's offset as written."
)
WANTS = [("updated is given with each note's own offset, not as UTC", True)]
# The plan names what sync.py reads of updated, so its form is a decision that rests on the fact; a
# plan that did not left the fact given unshown, in a trial of 2026-11-04.
FIRST = trial_pinner.FIRST.replace(
    "stop parsing its text.",
    "stop parsing its text, and sync.py still reads each note's time right.",
)
assert FIRST != trial_pinner.FIRST


def run(number: int) -> bool:
    """One run of the trial; prints what it found, and gives whether it passed and counted."""
    copies, repo, stream, turns = trial_pinner.tried(
        f"trial-corrected-{number}", FIRST, wider=True, found=FOUND, intent=INTENT
    )
    found = pinning.tree_and_untried(repo, stream)
    if not found:
        return False
    path = found[0]
    shown = any(t.get("shows_fact") and "UTC" in str(t["message"]) for t in turns)
    untried = [] if shown else ["no message showed the person that updated is in UTC"]
    wrong = trial_pinner.wrong_in(turns) + pinning.held(copies["pin"], path)
    wrong += pinning.slips(stream, repo, copies["pin"], turns)
    wrong += pinning.unheld(pinning.judged_tree(path, os.path.dirname(repo), WANTS), WANTS)
    return pinning.verdict(untried, wrong)


if __name__ == "__main__":
    pinning.main(run)
