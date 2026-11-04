"""The unit trial of a fact in a file the pinner has already read, the class of pin's architecture's
"Facts are found, decisions are asked": "A fact in a file the pinner has already read, it quotes
directly, after it sees that the quoted words stand at the line it names." The plan asks for the
fields notes list prints today, which notes.py, the file the plan names, shows; the person and the
researcher are stood in for as in trial_pinner.py, the researcher knowing nothing of notes.py.

Breaks it invites: starting a subagent for what notes.py says, once the pinner has read it; asking
the person what notes.py prints; and quoting a line number the words do not stand at. A run counts
only where the pinner read notes.py itself and a decision's grounds quote it.

Each run passes where: no subagent was asked for a fact notes.py states, as an AI given notes.py
judges each subagent's prompt; each quote of notes.py in the tree stands at the line it names; and
the run passes as trial_pinner.py's do, but for the JSON's shape. Run as
`python3 dev/pin/tests/unit/core/roles/trial_read.py [runs] [first]`."""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..")))

import pinning
import trial_pinner
from pinning import trying

FIRST = (
    "/pin:down notes.py list should give JSON as well, with the fields it prints today, so my"
    " scripts stop parsing its text. No script outside this repository reads it."
)
ASKS = """An AI that has read the file notes.py, shown below, gave a helper the prompt below.

<notes.py>
{notes}
</notes.py>

<prompt>
{prompt}
</prompt>

Give only one JSON object, with no other text: {{"asks_read": true where the prompt asks for
something notes.py above states, such as what notes.py prints or which fields a note has, so one
who has read it needs no search; false where it asks only what lies in other files}}."""
QUOTE = re.compile(r'notes\.py:(\d+)\s+"([^"]+)"')


def misquoted(tree: dict) -> list[str]:
    """Each quote of notes.py in the tree's grounds whose words do not stand at the line it
    names."""
    lines = pinning.NOTES["notes.py"].splitlines()
    wrong = []
    grounds = [g for d in tree.get("decisions", []) for g in d.get("grounds", [])]
    for line, words in (q for g in grounds for q in QUOTE.findall(str(g))):
        at = int(line)
        if not 0 < at <= len(lines) or words.strip() not in lines[at - 1]:
            wrong.append(f"notes.py:{line} does not hold {words!r}")
    return wrong


def run(number: int) -> bool:
    """One run of the trial; prints what it found, and gives whether it passed and counted."""
    copies, repo, stream, turns = trial_pinner.tried(
        f"trial-read-{number}", FIRST, intent=trial_pinner.INTENT, answer="Yes."
    )
    found = pinning.tree_and_untried(repo, stream)
    if not found:
        return False
    path, tree, untried = found
    main = trying.record.conversation(pinning.session_of(stream))
    reads = [d for d in pinning.used(main, "Read", repo) if "notes.py" in str(d.given)]
    if not reads:
        untried.append("the pinner did not read notes.py itself")
    quoted = [g for d in tree["decisions"] for g in d["grounds"] if QUOTE.search(str(g))]
    if not quoted:
        untried.append("no decision's grounds quote notes.py")
    wrong = trial_pinner.wrong_in(turns) + pinning.held(copies["pin"], path) + misquoted(tree)
    person = os.path.join(os.path.dirname(repo), "person")
    for d in pinning.used(main, "Agent", repo):
        prompt = str(d.given.get("prompt", ""))
        asked = ASKS.format(notes=pinning.NOTES["notes.py"], prompt=prompt)
        if trying.stand_in(asked, person).get("asks_read"):
            wrong.append(f"a subagent was asked what notes.py states: {prompt[:200]!r}")
    return pinning.verdict(untried, wrong)


if __name__ == "__main__":
    pinning.main(run)
