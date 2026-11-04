"""The prompt test of the pinner, `pin:down` alone, as pin's architecture's Test says: Claude
Code on Opus, with a copy of pin, is given `/pin:down` with the plan in the notes app's
repository; a script stands in for the person, answering "Yes." to every message, and a project
subagent named Explore, which Claude Code takes in place of its own, stands in for the
researcher, giving set facts. An AI given the person's intent judges each message, but answers
none.

Breaks it invites: those of trial_down.py, and asking the person a decision that follows from the
plan, as a "yes" to everything leaves the pinner no answer that tells it otherwise. A run counts
only where a decision rests on a fact quoted from scripts/, and check.py once named more than one
decision open at once.

Each run passes where: each message held one point; no message asked a fact of the repository or a
decision the AI could settle itself; a fact was shown to the person before the design, where a
decision rests on one; the design was shown to confirm; and the tree passes check.py with no
decision open. Run as `python3 dev/pin/tests/unit/core/roles/trial_pinner.py [runs] [first]`."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..")))

import pinning
from pinning import trying

FIRST = (
    "/pin:down notes list should give JSON as well, so my scripts stop parsing its text. No"
    " script outside this repository reads it."
)


def line_of(path: str, words: str) -> str:
    """`path:line "the line"`, for the first line of the notes app's file at the path that holds
    the words."""
    for number, line in enumerate(pinning.NOTES[path].splitlines(), 1):
        if words in line:
            return f'{path}:{number} "{line.strip()}"'
    raise SystemExit(f"{path} holds no {words!r}")


def researcher() -> str:
    """The stand-in for the researcher: a subagent named Explore that gives set facts, quoted as
    the notes app's files hold them, for whatever it is asked."""
    facts = [
        "scripts/sync.py and scripts/export.py run `notes.py list` and split each line on tabs:",
        "- " + line_of("scripts/sync.py", 'split("\\t")'),
        "- " + line_of("scripts/export.py", 'split("\\t")'),
        "sync.py reads updated as ISO 8601:",
        "- " + line_of("scripts/sync.py", "fromisoformat"),
        "No other file runs `notes.py list`.",
    ]
    return (
        "---\nname: Explore\ndescription: Finds facts in the repository. Use to look something"
        " up.\ntools: Read\n---\n\nGive back these facts, word for word, whatever you are asked,"
        " and nothing else; where they do not answer what you are asked, say so.\n\n"
        + "\n".join(facts)
        + "\n"
    )


def run(number: int) -> bool:
    """One run of the prompt test; prints what it found, and gives whether it passed and
    counted."""
    place = trying.folder("pin", f"trial-pinner-{number}")
    repo, copies = pinning.made(place, {})
    os.makedirs(os.path.join(repo, ".claude", "agents"))
    with open(os.path.join(repo, ".claude", "agents", "Explore.md"), "w", encoding="utf-8") as f:
        f.write(researcher())
    stream = os.path.join(place, "stream.jsonl")
    turns = pinning.conversed([copies["pin"]], repo, FIRST, place, stream, answer="Yes.")
    found = pinning.tree_and_untried(repo, stream)
    if not found:
        return False
    path, _, untried = found
    wrong = []
    for n, t in enumerate(turns, 1):
        if int(t.get("points") or 0) > 1:
            wrong.append(f"message {n} put {t['points']} points to the person")
        for key, what in (("asks_fact", "a fact"), ("asks_not_theirs", "what it could settle")):
            if t.get(key):
                wrong.append(f"message {n} asked the person {what}")
    designed = next((n for n, t in enumerate(turns) if t.get("confirms_design")), None)
    if designed is None:
        wrong.append("the design was not shown to the person to confirm")
    elif not any(t.get("shows_fact") for t in turns[:designed]):
        wrong.append("no fact was shown to the person before the design")
    return pinning.verdict(untried, wrong + pinning.held(copies["pin"], path))


if __name__ == "__main__":
    pinning.main(run)
