"""The unit trial of a design the person changes, the step of pin's architecture's first sequence
"the person changes something": shown the whole design, the person changes their mind on the JSON's
shape, from one array to one object a line, and the pinner opens that decision again, with each that
builds on it, and goes back to the loop. The researcher is stood in for as in trial_pinner.py; the
person, by an AI that answers from an intent never shown pin.

Breaks it invites: writing the change into the shape alone, leaving decided what builds on it;
asking the person again what they have just said; and ending on the change with no design shown
again.

Each run passes where: after a check of the main conversation found no decision open, a later one
found the tree to hold with a decision open, so each decision building on one reopened was open
too; the design was shown again after the change; the tree holds the person's new wants, the
shape decided by them; and the run passes as trial_pinner.py's do. Run as
`python3 dev/pin/tests/unit/core/roles/trial_change.py [runs] [first]`."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..")))

import pinning
import trial_pinner
import trial_reopen

INTENT = trial_pinner.INTENT + (
    "\n\nOne thing changes during the conversation. The first time you are shown the whole design"
    " and asked whether you understand it the same way, you change your mind on the JSON's shape:"
    " you now want one object per line, JSON Lines, so sync.py can read the notes as they come."
    " Say so as what is to change. From then on that is what you want, and being asked it again"
    " wastes your time."
)


def reopened(outputs: list[str]) -> bool:
    """Whether, after a check found no decision open, a later one found the tree to hold with a
    decision open."""
    done = next((n for n, out in enumerate(outputs) if "No decision is open." in out), None)
    if done is None:
        return False
    return any(" holds: " in out and "Open to decide now: " in out for out in outputs[done:])


def run(number: int) -> bool:
    """One run of the trial; prints what it found, and gives whether it passed and counted."""
    copies, repo, stream, turns = trial_pinner.tried(
        f"trial-change-{number}", trial_pinner.FIRST, intent=INTENT
    )
    found = pinning.tree_and_untried(repo, stream)
    if not found:
        return False
    path, untried = found[0], []
    changed = next((n for n, t in enumerate(turns) if t.get("changes_design")), None)
    if changed is None:
        untried.append("the person changed nothing of the design")
    wrong = trial_pinner.wrong_in(turns) + pinning.slips(stream, repo, copies["pin"], turns)
    if not reopened(pinning.main_outputs(stream, repo)):
        wrong.append("no check found the tree to hold with a decision reopened")
    if changed is not None and not any(t.get("confirms_design") for t in turns[changed + 1 :]):
        wrong.append("the design was not shown again after the change")
    place = os.path.dirname(repo)
    wrong += pinning.held(copies["pin"], path)
    wrong += pinning.unheld(
        pinning.judged_tree(path, place, trial_reopen.WANTS), trial_reopen.WANTS
    )
    return pinning.verdict(untried, wrong)


if __name__ == "__main__":
    pinning.main(run)
