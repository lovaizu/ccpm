"""The E2E test of O2 of pin's UX, "Turn has the design of a work pinned down": a plugin standing in
for Turn or rn, `maker`, kept beside this file, declares pin in its dependencies, and its subagent
`designer` takes `pin:down` by its frontmatter and pins down the notes app's `--json` option from a
tree that holds the goal, three questions, of which the JSON's form and the scripts' change are
decided apart, so more than one decision is open at once, and one decision already settled. Claude
Code runs on Opus with copies of pin and of maker; the main conversation starts designer and puts
each of its messages to the person, stood in for by an AI that answers from an intent written
beforehand and never shown pin.

Breaks it invites, beside those of trial_down.py: asking the person again what maker settled, the
goal and the text staying the default; and running the check in a form other than the one pin's
architecture promises. A run counts only where, beside what trial_down.py's runs count on,
designer ran the check.

Each run passes where, beside what trial_down.py's runs pass on: each run of the check by designer
is `python3 <pin's folder>/scripts/check.py <path>`, word for word; and the decision maker settled
is in the tree as it was given. Run as
`python3 dev/pin/tests/e2e/trial_caller.py [runs] [first]`."""

from __future__ import annotations

import json
import os
import re

import pinning
from pinning import trying

MAKER = os.path.join(pinning.HERE, "maker")
FIRST = (
    "Start the subagent maker:designer to design a `--json` option on `notes list` in this"
    " repository. Whenever it ends with a message headed `For the person:`, give me that message"
    " word for word as your whole reply. When I answer, resume designer with SendMessage, its"
    f" message `{trying.ANSWERED}` and my answer word for word on the next line, and wait for it."
    " Do nothing else yourself. When designer ends with"
    " no message for the person, reply with what it gave back."
)
INTENT = pinning.INTENT + (
    "\n\nYou already told maker, the tool that designs the change, the goal above, and that the"
    " text output stays the default with JSON only under --json. Being asked either again wastes"
    " your time."
)
SETTLED = "the text stays the default; JSON only with --json"


def run(number: int) -> bool:
    """One run of the E2E test; prints what it found, and gives whether it passed and counted."""
    place = trying.folder("pin", f"trial-caller-{number}")
    repo, copies = pinning.made(place, {"maker": MAKER})
    stream = os.path.join(place, "stream.jsonl")
    turns = pinning.conversed(
        [copies["pin"], copies["maker"]], repo, FIRST, place, stream, intent=INTENT
    )
    path = os.path.join(repo, ".maker", "notes-json", "design-tree.json")
    if not os.path.exists(path):
        print(f"  failed: no design tree at {path}")
        return False
    with open(path, encoding="utf-8") as f:
        tree = json.load(f)
    session = pinning.session_of(stream)
    designers = [
        a for a in trying.agents(session) if trying.record.agent_type(a) == "maker:designer"
    ]
    runs = [r for a in designers for r in pinning.check_outputs(a, repo)]
    untried = pinning.tried_in(tree, [out for _, out in runs])
    if not runs:
        untried.append("designer never ran the check")
    form = re.compile(re.escape(f"python3 {copies['pin']}/scripts/check.py ") + r"\S+")
    wrong = [f"the check was run as {c!r}" for c, _ in runs if not form.fullmatch(c.strip())]
    wrong += pinning.judged(copies["pin"], path, place, turns)
    if not any(d.get("decided") == SETTLED for d in tree.get("decisions", [])):
        wrong.append("the decision maker settled is not in the tree as given")
    return pinning.verdict(untried, wrong)


if __name__ == "__main__":
    pinning.main(run)
