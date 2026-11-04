"""The prompt test of the pinner, `pin:down` alone, as pin's architecture's Test says: Claude
Code on Opus, with a copy of pin, is given `/pin:down` with the plan in the notes app's
repository; a script stands in for the person, answering "Yes." to every message, and a project
subagent named Explore, which Claude Code takes in place of its own, stands in for the
researcher, giving set facts. An AI given the person's intent judges each message, but answers
none.

The classes it tries: a fact a search finds, which the pinner shows and does not ask; a fact only
the person knows, given in the first message, which it does not ask again; a decision the pinner
settles, which it does not ask; and a decision that is the person's, the JSON's shape, one array
or one object a line, which it asks.

Breaks it invites: those of trial_down.py, and asking the person a decision that follows from the
plan, as a "yes" to everything leaves the pinner no answer that tells it otherwise. A run counts
only where a decision rests on a fact quoted from scripts/, and check.py once named more than one
decision open at once.

The repository holds, beside the app, sixteen tools and their notes that do not run
`notes.py list`, so which scripts run it is a fact a search finds.

Each run passes where: the researcher was started; each message held one point; no message asked a
fact of the repository, a decision the AI could settle itself, or what the person had said; a fact
was shown to the person before the design, where a decision rests on one; the design was shown to
confirm; the JSON's shape is decided by the person; the tree passes check.py with no decision
open; and the run kept to the steps as pinning.slips judges it: no decision decided before one it
builds on, the tree named by no command but the check, and each decision put in its five lines.
Run as `python3 dev/pin/tests/unit/core/roles/trial_pinner.py [runs] [first]`."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
# What the trials of more than one level share lies in tests/.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..")))

import pinning
from pinning import trying

FIRST = (
    "/pin:down notes list should give JSON as well, so my scripts stop parsing its text. No"
    " script outside this repository reads it."
)
INTENT = pinning.INTENT + (
    "\n\nYou told the AI in your first message that no script outside this repository reads"
    " notes list. Being asked it again wastes your time."
)
# The person's decision of the plan: two ways serve the goal alike.
WANTS = [("the JSON's shape is decided: one array of objects, or one object per line", True)]
# Tools and notes beside the app, none running `notes.py list`, so the repository is too big to read
# whole and which scripts read the list is a fact a search must find.
TOOLS = ("backup", "stats", "lint", "rename", "archive", "dedupe", "spell", "wordcount")
TOOLS += ("index", "prune", "tagcloud", "mirror", "rotate", "digest", "verify", "compact")
WIDER = {
    **{
        f"tools/{name}.py": f'"""{name}: works on the Markdown files in notes/ directly."""\n\n'
        "import pathlib\n\n\n"
        "def main():\n"
        '    for path in sorted(pathlib.Path("notes").glob("*.md")):\n'
        f'        print("{name}", path.name, len(path.read_text()))\n'
        for name in TOOLS
    },
    **{f"docs/{name}.md": f"# {name}\n\nHow tools/{name}.py treats notes/.\n" for name in TOOLS},
}


def tried(
    name: str, first: str, wider: bool = False, found: tuple[str, ...] = (), **talk: Any
) -> tuple[dict[str, str], str, str, list[Any]]:
    """One conversation of `pin:down` alone in the notes app's repository, from the first message,
    in the folder of the trial's name, with the stand-in for the researcher laid there, giving the
    facts found beside its own, the person as talk names, and, where wider, WIDER committed beside
    the app; gives the copies' folders, the repository, the stream and the turns."""
    place = trying.folder("pin", name)
    repo, copies = pinning.made(place, {})
    if wider:
        for path, text in WIDER.items():
            os.makedirs(os.path.dirname(os.path.join(repo, path)), exist_ok=True)
            with open(os.path.join(repo, path), "w", encoding="utf-8") as f:
                f.write(text)
        who = ["-c", "user.name=e2e", "-c", "user.email=e2e@example.com"]
        subprocess.run(["git", "-C", repo, "add", "."], check=True)
        subprocess.run(["git", "-C", repo, *who, "commit", "-q", "-m", "tools"], check=True)
    pinning.researched(repo, found)
    stream = os.path.join(place, "stream.jsonl")
    turns = pinning.conversed([copies["pin"]], repo, first, place, stream, **talk)
    return copies, repo, stream, turns


def wrong_in(turns: list[dict[str, Any]]) -> list[str]:
    """What the person's view of the messages finds wrong: a message of more than one point, one
    that asks a fact, what the pinner could settle or what was said, no design shown, or no fact
    shown before it."""
    wrong = []
    keys = (("asks_fact", "a fact"), ("asks_not_theirs", "what it could settle"))
    keys += (("asks_settled", "again what was said"),)
    for n, t in enumerate(turns, 1):
        if int(t.get("points") or 0) > 1:
            wrong.append(f"message {n} put {t['points']} points to the person")
        for key, what in keys:
            if t.get(key):
                wrong.append(f"message {n} asked the person {what}")
    designed = next((n for n, t in enumerate(turns) if t.get("confirms_design")), None)
    if designed is None:
        wrong.append("the design was not shown to the person to confirm")
    elif not any(t.get("shows_fact") for t in turns[:designed]):
        wrong.append("no fact was shown to the person before the design")
    return wrong


def run(number: int) -> bool:
    """One run of the prompt test; prints what it found, and gives whether it passed and
    counted."""
    copies, repo, stream, turns = tried(
        f"trial-pinner-{number}", FIRST, wider=True, intent=INTENT, answer="Yes."
    )
    found = pinning.tree_and_untried(repo, stream)
    if not found:
        return False
    path, _, untried = found
    wrong = wrong_in(turns) + pinning.held(copies["pin"], path)
    wrong += pinning.slips(stream, repo, copies["pin"], turns)
    agents = trying.agents(pinning.session_of(stream))
    if not any(trying.record.agent_type(a) == "Explore" for a in agents):
        wrong.append("no researcher was started for the fact a search finds")
    wrong += pinning.unheld(pinning.judged_tree(path, os.path.dirname(repo), WANTS), WANTS)
    return pinning.verdict(untried, wrong)


if __name__ == "__main__":
    pinning.main(run)
