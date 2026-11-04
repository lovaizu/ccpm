"""The unit trial of a fact only the person knows, the class of pin's architecture's "Facts are
found, decisions are asked" that the pinner must ask: "What only the person knows, such as what
lies outside the repository, is theirs to tell: ask it as a point of its own". The plan asks for
JSON in place of the text, and whether the text may go rests on what reads it outside the
repository, which no search finds: a job on the person's server greps it. The researcher is stood
in for as in trial_pinner.py; the person, by an AI that answers from an intent never shown pin,
telling of the job only when asked what outside the repository reads the output.

Breaks it invites: taking for granted that nothing outside the repository reads the text, as the
repository shows no other reader, and dropping the text; and asking it within another point.

Each run passes where: a message asked the person what outside the repository reads notes list,
as an AI judges the messages; the tree keeps the text output for that job; and the run passes as
trial_pinner.py's do, but for the JSON's shape. Run as
`python3 dev/pin/tests/unit/core/roles/trial_outside.py [runs] [first]`."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..")))

import pinning
import trial_pinner
from pinning import trying

FIRST = "/pin:down notes list should give JSON instead of its text, so my scripts stop parsing it"
WANT = (
    "- JSON only with a `--json` option; the text output stays the default, as you read it by eye."
)
assert WANT in pinning.INTENT
INTENT = pinning.INTENT.replace(
    WANT,
    '- You wrote "instead of" loosely. A cron job on your server, outside this repository, runs\n'
    "  `python3 notes.py list` each night and greps its text, so the text output must stay the\n"
    "  default, with JSON only under an option. Tell of the job only where you are asked what\n"
    "  outside the repository reads the output; asked only whether to keep the text, say the AI\n"
    "  may decide it.",
)
WANTS = [
    ("the text output stays the default, for a job outside the repository that reads it", False)
]
ASKS = """Here are the messages a planning AI sent a person, numbered:

{messages}

Give only one JSON object, with no other text: {{"asking": the numbers of the messages that ask the
person what outside the repository, such as a job or a script elsewhere, reads the output of notes
list, as a list of numbers, empty where none does}}."""


def run(number: int) -> bool:
    """One run of the trial; prints what it found, and gives whether it passed and counted."""
    copies, repo, stream, turns = trial_pinner.tried(
        f"trial-outside-{number}", FIRST, intent=INTENT
    )
    found = pinning.tree_and_untried(repo, stream)
    if not found:
        return False
    path, _, _ = found
    place = os.path.dirname(repo)
    wrong = trial_pinner.wrong_in(turns) + pinning.held(copies["pin"], path)
    wrong += pinning.unheld(pinning.judged_tree(path, place, WANTS), WANTS)
    messages = "\n\n".join(f"{n}. {t['message']}" for n, t in enumerate(turns, 1))
    asking = trying.stand_in(ASKS.format(messages=messages), os.path.join(place, "person"))
    if not asking.get("asking"):
        wrong.append("no message asked the person what outside the repository reads notes list")
    return pinning.verdict([], wrong)


if __name__ == "__main__":
    pinning.main(run)
