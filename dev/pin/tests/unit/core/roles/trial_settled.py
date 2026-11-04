"""The unit trial of a tree a caller settled part of, the case of pin's architecture's "pin knows no
caller": "A caller gives `pin:down` the goal, the questions the work must answer and the path of the
tree, and the decisions it has already settled; pin fills the rest. A caller may add keys of its
own to the tree". The plugin made for the test, maker, kept in ../../../ux/maker/, stands in for
the caller: its subagent designer takes `pin:down` from a tree holding the goal, three questions,
one decision the person settled with maker, and a key of maker's own. The main conversation puts
each of designer's messages to the person, for whom a script stands in, answering "Yes."; the
researcher is stood in for as in trial_pinner.py, and an AI given the person's intent, which says
what maker settled, judges each message.

Breaks it invites: asking the person again the goal or the decision maker settled; asking what the
pinner could settle; and dropping or changing what maker wrote. A run counts as trial_caller.py's
do.

Each run passes where: designer's checks and the tree pass as trial_caller.py's do, the key of
maker's own kept; no message asked again what maker settled; and the run passes as
trial_pinner.py's do. Run as `python3 dev/pin/tests/unit/core/roles/trial_settled.py [runs]
[first]`."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..")))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "ux")))

import pinning
import trial_caller
import trial_pinner
from pinning import trying


def run(number: int) -> bool:
    """One run of the trial; prints what it found, and gives whether it passed and counted."""
    place = trying.folder("pin", f"trial-settled-{number}")
    repo, copies = pinning.made(place, {"maker": trial_caller.MAKER})
    pinning.researched(repo)
    stream = os.path.join(place, "stream.jsonl")
    plugins = [copies["pin"], copies["maker"]]
    talk = {"intent": trial_caller.INTENT, "answer": "Yes."}
    turns = pinning.conversed(plugins, repo, trial_caller.FIRST, place, stream, **talk)
    found = trial_caller.designed(copies["pin"], repo, stream)
    if not found:
        return False
    path, untried, wrong = found
    wrong += trial_pinner.wrong_in(turns) + pinning.held(copies["pin"], path)
    return pinning.verdict(untried, wrong)


if __name__ == "__main__":
    pinning.main(run)
