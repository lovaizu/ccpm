"""The E2E test of a decision reopened, the story of pin's architecture "As Turn or rn, I want to
reopen one decision with `pin:down`, and have it and each decision that builds on it decided
again": the notes app's repository holds the design tree of its `--json` option, every decision
settled, and maker's subagent `reviser`, kept beside this file, takes `pin:down` to reopen D2, the
JSON's shape, as the person has changed their mind. The main conversation puts each of reviser's
messages to the person, stood in for by an AI that answers from an intent never shown pin.

Breaks it invites: reopening D2 alone, leaving decided what builds on it; asking again what does
not build on D2; and leaving the shape as it was. A run counts only where reviser ran the check.

Each run passes where: a run of the check by reviser found the tree to hold with D2 open, so every
decision building on D2 was open too; D1, which does not build on D2, is as it was; D2 is decided
anew by the person, as one JSON object a line; and the conversation passes as trial_caller.py's
runs do, against the person's new wants. Run as
`python3 dev/pin/tests/e2e/trial_reopen.py [runs] [first]`."""

from __future__ import annotations

import json
import os
import re

import pinning
import trial_caller
from pinning import trying

TREE = ".maker/notes-json/design-tree.json"
FIRST = trial_caller.FIRST.replace(
    "Start the subagent maker:designer to design a `--json` option on `notes list`",
    "Start the subagent maker:reviser to reopen D2, the JSON's shape, of the design of the"
    " `--json` option on `notes list`, as the person has changed their mind about it,",
)
INTENT = pinning.INTENT.replace(
    "- The JSON is one array of objects, one object per note, so `jq` reads it whole;"
    " not one object\n  per line.",
    "- The JSON is one object per line, one line per note, as JSON Lines, so sync.py can read the\n"
    "  notes as they come. You first chose one array, and have changed your mind; you told maker\n"
    "  so, and that you want the shape looked at again.",
) + (
    "\n\nYou settled with maker before: the goal, and that the text output stays the default with"
    " JSON only under --json. Being asked either again wastes your time."
)
WANTS = [
    (want, theirs)
    if "array" not in want
    else ("the JSON is one object per line, one per note, not one array", True)
    for want, theirs in pinning.WANTS
]
SETTLED = {
    "D1": (
        "Whether the text output stays the default",
        ["Q2"],
        [],
        "the text stays the default; JSON only with --json",
        "user",
        ["the person, 2026-11-02"],
    ),
    "D2": (
        "The JSON's shape: one array, or one object per line",
        ["Q1"],
        [],
        "one JSON array holding every note",
        "user",
        ["the person, 2026-11-02"],
    ),
    "D3": (
        "Which fields each note has",
        ["Q1"],
        ["D2"],
        "id, title, tags and updated",
        "reasoning",
        ["D2", "notes.py:1 the fields the text output shows"],
    ),
    "D4": (
        "How tags appear",
        ["D3"],
        ["D3"],
        "a list of texts",
        "reasoning",
        ["D3", "the goal: scripts stop parsing text"],
    ),
    "D5": (
        "How updated appears",
        ["D3"],
        ["D3"],
        "the same ISO 8601 text as the text output",
        "reasoning",
        ["D3", "sync.py reads it with datetime.fromisoformat"],
    ),
    "D6": (
        "Whether the scripts switch to --json in this change",
        ["Q1"],
        ["D2"],
        "yes, both",
        "reasoning",
        ["D2", "the goal: scripts stop parsing text"],
    ),
}


def written() -> dict:
    """The design tree as the person and maker left it, every decision settled."""
    keys = ("what", "contributes_to", "builds_on", "decided", "settled_by", "grounds")
    return {
        "goal": {
            "what": "Scripts that read `notes list` get its notes as JSON, so they stop parsing"
            " text.",
            "grounds": ["the person, 2026-11-02"],
        },
        "questions": [
            {"id": "Q1", "what": "Can each script that reads notes list read the JSON as it is?"},
            {"id": "Q2", "what": "Do people who read notes list by eye see the same as before?"},
        ],
        "decisions": [{"id": i, **dict(zip(keys, v))} for i, v in SETTLED.items()],
    }


def run(number: int) -> bool:
    """One run of the E2E test; prints what it found, and gives whether it passed and counted."""
    place = trying.folder("pin", f"trial-reopen-{number}")
    repo, copies = pinning.made(place, {"maker": trial_caller.MAKER})
    path = os.path.join(repo, TREE)
    os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(written(), f, indent=1)
    before = written()["decisions"][0]
    stream = os.path.join(place, "stream.jsonl")
    turns = pinning.conversed(
        [copies["pin"], copies["maker"]], repo, FIRST, place, stream, intent=INTENT
    )
    with open(path, encoding="utf-8") as f:
        tree = json.load(f)
    session = pinning.session_of(stream)
    revisers = [a for a in trying.agents(session) if trying.record.agent_type(a) == "maker:reviser"]
    runs = [out for a in revisers for _, out in pinning.check_outputs(a, repo)]
    untried = [] if runs else ["reviser never ran the check"]
    wrong = []
    if not any(
        " holds: " in out and re.search(r"Open to decide now: .*\bD2\b", out) for out in runs
    ):
        wrong.append("no check found the tree to hold with D2 open")
    by_id = {d["id"]: d for d in tree["decisions"]}
    if by_id.get("D1") != before:
        wrong.append(f"D1 changed: {by_id.get('D1')}")
    d2 = by_id.get("D2", {})
    if d2.get("settled_by") != "user" or d2.get("decided") == SETTLED["D2"][3]:
        wrong.append(f"D2 was not decided anew by the person: {d2}")
    wrong += pinning.judged(copies["pin"], path, place, turns, WANTS)
    return pinning.verdict(untried, wrong)


if __name__ == "__main__":
    pinning.main(run)
