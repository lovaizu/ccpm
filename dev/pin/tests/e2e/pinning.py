"""What pin's E2E tests stand on: the repository of the notes app `notes`, the plan the README's
walkthrough pins; a copy of pin for each run; the person, stood in for by an AI that answers from
the intent written for it, never shown pin's skill, and says of each message what it put to them;
the conversation gone on until the person has confirmed the design; and the design tree judged,
by check.py and by an AI given the intent, as the person would judge it."""

from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "dev", "lane", "trials"))

import trying

PIN = os.path.join(ROOT, "plugins", "pin")
# The most messages put to the person before a run is stopped as one that does not end.
TURNS = 24
# The notes app: notes.py prints each note as a line of tab-separated fields, and two scripts read
# that text; sync.py reads `updated` as ISO 8601, the fact a pinner is to find.
NOTES = {
    "README.md": "# notes\n\nKeeps notes as Markdown files. `python3 notes.py list` lists them.\n",
    "notes.py": (
        '"""notes: `python3 notes.py list` prints each note as id, title, tags and updated,'
        ' tab-separated."""\n\nimport sys\n\nNOTES = [\n'
        '    ("1", "Groceries", ["home"], "2026-11-01T09:30:00+00:00"),\n'
        '    ("2", "Trip plan", ["travel", "family"], "2026-11-02T18:05:00+00:00"),\n]\n\n\n'
        "def main(argv):\n"
        '    if argv[:1] != ["list"]:\n'
        '        print("usage: notes.py list")\n'
        "        return 2\n"
        "    for id, title, tags, updated in NOTES:\n"
        '        print("\\t".join([id, title, ",".join(tags), updated]))\n'
        "    return 0\n\n\n"
        'if __name__ == "__main__":\n'
        "    sys.exit(main(sys.argv[1:]))\n"
    ),
    "scripts/sync.py": (
        '"""Sends each note changed since the last sync to the calendar."""\n\n'
        "import subprocess\nfrom datetime import datetime\n\nLAST = datetime(2026, 11, 1)\n\n\n"
        "def changed():\n"
        "    out = subprocess.run(\n"
        '        ["python3", "notes.py", "list"], capture_output=True, text=True\n'
        "    )\n"
        "    found = []\n"
        "    for line in out.stdout.splitlines():\n"
        '        fields = line.split("\\t")\n'
        "        if datetime.fromisoformat(fields[3]).replace(tzinfo=None) > LAST:\n"
        "            found.append(fields[1])\n"
        "    return found\n"
    ),
    "scripts/export.py": (
        '"""Writes the notes\' titles and tags to notes.csv."""\n\n'
        "import subprocess\n\n\n"
        "def export():\n"
        "    out = subprocess.run(\n"
        '        ["python3", "notes.py", "list"], capture_output=True, text=True\n'
        "    )\n"
        '    with open("notes.csv", "w") as f:\n'
        "        for line in out.stdout.splitlines():\n"
        '            id, title, tags, _ = line.split("\\t")\n'
        '            f.write(f"{title},{tags}\\n")\n'
    ),
}
# What the person truly wants, and what they know, written before the run and never shown to pin.
INTENT = """You are the developer of a small notes app, `notes`, in the repository the AI works in.
You want `python3 notes.py list` to give JSON as well, so that your scripts stop parsing text.

What you want, which the AI may or may not ask:
- JSON only with a `--json` option; the text output stays the default, as you read it by eye.
- The JSON is one array of objects, one object per note, so `jq` reads it whole; not one object
  per line.
- Each object has the fields id, title, tags and updated, as the text output has them.
- tags is a list of texts in the JSON, not one text with commas.
- updated stays the same ISO 8601 text as the text output gives today.

What you know of your repository, which the AI can read for itself: notes.py prints the notes;
scripts/sync.py and scripts/export.py run `notes.py list` and split its text; sync.py reads updated
with datetime.fromisoformat.

How you answer: briefly, as a busy developer, in the language the AI writes to you in. Answer what
you are asked from what you want above. Where a fact is shown to you, say whether it is right. Where
you are asked something your wants above do not settle, say the AI may decide it. Where you are
shown the whole design and asked whether you understand it the same way, say yes where it holds
what you want above, and otherwise say what is to change."""
# The intent's points, each with whether it is the person's to decide, for the judge of the tree.
WANTS = [
    ("JSON is given only with a --json option, and the text output stays the default", False),
    ("the JSON is one array of objects, one per note, not one object per line", True),
    ("each object has id, title, tags and updated", False),
    # A list follows from the goal, as a text with commas is still text to parse.
    ("tags is a list of texts in the JSON", False),
    ("updated is the same ISO 8601 text as the text output gives", False),
]
FINDS = trying.finds(
    """You stand in for the person a planning AI is talking with. Here is who you are and what
you truly want; the AI cannot see it:""",
    """- "answer": your answer to the message, as you would write it;
"""
    + trying.POINTS
    + """
- "asks_fact": true where the message asks you something about the repository that the AI could
  read for itself, rather than showing you what it found for you to confirm; otherwise false;
- "asks_settled": true where it asks you again something you are said, above, to have settled
  already, or something you already answered in this conversation; otherwise false;
- "shows_fact": true where it shows you a fact it found, for you to confirm; otherwise false;
- "asks_not_theirs": true where it asks you to decide something that follows from what you want,
  the facts and what you said, so the AI could have settled it itself; otherwise false;
- "confirms_design": true where it shows you the whole design and asks whether you understand it
  the same way; otherwise false;
- "finished": true where the message asks you nothing and says the planning is done; otherwise
  false.""",
)
JUDGES = """A planning AI has written a design tree for a plan. The person whose plan it is wanted
the points below. For each point, judge whether a decision of the tree holds it as the person wants
it, and by whom that decision was settled.

The points:
{wants}

The design tree:
{tree}

Give only one JSON object, with no other text: {{"points": [{{"point": <its number>, "held": true
or false, "settled_by": the settled_by of the decision that holds it, or null}}]}}, one entry for
each point, in order."""


asked = trying.stand_in


def made(place: str, plugins: dict[str, str]) -> tuple[str, dict[str, str]]:
    """The repository of the run, `notes` in its folder, with the notes app committed, and a copy
    of pin and of each plugin given by its folder beside it, by name; gives the repository and the
    copies' folders, pin's under "pin"."""
    repo = os.path.join(place, "notes")
    trying.committed(repo, NOTES)
    copies = {}
    for name, source in {"pin": PIN, **plugins}.items():
        copies[name] = os.path.join(place, "plugins", name)
        shutil.copytree(source, copies[name])
    return repo, copies


def talked(
    conversation: trying.Conversation,
    first: str,
    place: str,
    stream: str,
    intent: str = INTENT,
    before: list[dict[str, Any]] | None = None,
    answer: str | None = None,
    stop_after: int | None = None,
) -> list[dict[str, Any]]:
    """Each message the AI put to the person, with what the person said of it, from the first
    message sent until the person has confirmed the design and the AI has replied, or the AI says it
    is done; the person answers from the intent, in a folder of its own in the run's folder,
    remembering the turns before of an earlier conversation. Where answer is given, a script sends
    it to every message in place of the person, who still judges each; where stop_after is, the
    person leaves the conversation after so many answers, as one who stops."""
    alone = os.path.join(place, "person")
    os.makedirs(alone, exist_ok=True)
    said = [
        f"{who}: {t[key]}"
        for t in before or []
        for who, key in (("AI", "message"), ("You", "answer"))
    ]
    turns: list[dict[str, Any]] = []
    reply = conversation.send(first, stream, idle=True)
    for _ in range(TURNS):
        message = str(reply.get("result", ""))
        heard = trying.heard(FINDS, intent, said, message, alone)
        if answer is not None:
            heard["answer"] = answer
        turns.append({"message": message, **heard})
        print(f"  AI: {message[:300]!r}")
        print(f"  person: {str(heard.get('answer'))[:200]!r} {heard_of(heard)}")
        # The AI's reply to the person's answer on the design ends the run, unless it shows the
        # design again, as after a change the person asked for.
        after_design = len(turns) > 1 and turns[-2].get("confirms_design")
        if heard.get("finished") or (after_design and not heard.get("confirms_design")):
            return turns
        said += [f"AI: {message}", f"You: {heard['answer']}"]
        reply = conversation.send(str(heard["answer"]), stream, idle=True)
        # The person leaves once the AI has taken in their last answer, its reply unread.
        if stop_after is not None and len(turns) >= stop_after:
            return turns
    raise SystemExit(f"the conversation did not end in {TURNS} messages")


def conversed(
    plugins: list[str], repo: str, first: str, place: str, stream: str, **talk: Any
) -> list[dict[str, Any]]:
    """The turns of one conversation of Claude Code on the copies of the plugins in the repository,
    as talked gives them with what talk names; printing how many there were and the time taken."""
    started = time.monotonic()
    conversation = trying.Conversation(plugins, repo, wait=8)
    try:
        turns = talked(conversation, first, place, stream, **talk)
    finally:
        conversation.close()
    print(f"  {len(turns)} messages, {time.monotonic() - started:.0f} s")
    return turns


def tree_and_untried(repo: str, stream: str) -> tuple[str, dict[str, Any], list[str]] | None:
    """The path and the design tree of the one tree in the repository's .pin/, with the invited
    breaks the run did not meet, as tried_in gives them from the main conversation's checks; None,
    printing why, where there is not one tree alone."""
    found = pinned(repo)
    if not found:
        return None
    return found[0], found[1], tried_in(found[1], main_outputs(stream, repo))


def session_of(stream: str) -> str:
    """The session's ID, from the first line of the stream Claude Code printed."""
    with open(stream, encoding="utf-8") as f:
        return json.loads(f.readline())["session_id"]


def heard_of(heard: dict[str, Any]) -> str:
    """What the person said of a message, in a few words."""
    keys = ("points", "asks_fact", "asks_settled", "shows_fact", "asks_not_theirs")
    keys += ("confirms_design", "finished")
    return " ".join(f"{k}={heard.get(k)}" for k in keys)


def checked(pin: str, path: str) -> subprocess.CompletedProcess:
    """check.py of the copy of pin run on the tree at the path."""
    command = [sys.executable, os.path.join(pin, "scripts", "check.py"), path]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def judged_tree(
    path: str, place: str, wanted: list[tuple[str, bool]] | None = None
) -> list[dict[str, Any]]:
    """For each of the intent's points, or each point wanted, whether the tree at the path holds it
    and who settled it, as an AI judges it given the points and the tree."""
    with open(path, encoding="utf-8") as f:
        tree = f.read()
    wants = "\n".join(f"{n}. {w}" for n, (w, _) in enumerate(wanted or WANTS, 1))
    return asked(JUDGES.format(wants=wants, tree=tree), os.path.join(place, "person"))["points"]


def wrong_in(
    turns: list[dict[str, Any]],
    points: list[dict[str, Any]],
    wanted: list[tuple[str, bool]] | None = None,
) -> list[str]:
    """What the person's view of the messages and the judge of the tree find wrong: a message of
    more than one point, a fact asked, a settled point asked again, no design shown to confirm, a
    point the tree does not hold, or one of the person's settled without them."""
    wrong = []
    for n, t in enumerate(turns, 1):
        if int(t.get("points") or 0) > 1:
            wrong.append(f"message {n} put {t['points']} points to the person")
        if t.get("asks_fact"):
            wrong.append(f"message {n} asked the person a fact of the repository")
        if t.get("asks_settled"):
            wrong.append(f"message {n} asked again what was settled")
    if not any(t.get("confirms_design") for t in turns):
        wrong.append("the design was not shown to the person to confirm")
    for p, (want, theirs) in zip(points, wanted or WANTS):
        if not p.get("held"):
            wrong.append(f"the tree does not hold: {want}")
        elif theirs and p.get("settled_by") != "user":
            wrong.append(f"settled without the person: {want} ({p.get('settled_by')})")
    return wrong


def tried_in(tree: dict[str, Any], outputs: list[str]) -> list[str]:
    """Which invited break the run did not meet: a fact of the repository a decision rests on, and
    more than one decision open to decide at once, from the tree and check.py's outputs."""
    untried = []
    # A fact found may settle a decision of its own, or be one ground among others of one.
    quoted = re.compile(r"scripts/\w+\.py:\d+")
    if not any(quoted.search(" ".join(d.get("grounds", []))) for d in tree.get("decisions", [])):
        untried.append("no decision rests on a fact quoted from scripts/")
    if not any(re.search(r"Open to decide now: \S+, ", out) for out in outputs):
        untried.append("check.py never named more than one decision open at once")
    return untried


def pinned(repo: str) -> tuple[str, dict[str, Any]] | None:
    """The path and the design tree of the one tree in the repository's .pin/; None, printing why,
    where there is not one alone."""
    trees = glob.glob(os.path.join(repo, ".pin", "*", "design-tree.json"))
    if len(trees) != 1:
        print(f"  failed: not one design tree in .pin/: {trees}")
        return None
    with open(trees[0], encoding="utf-8") as f:
        return trees[0], json.load(f)


def main_outputs(stream: str, repo: str) -> list[str]:
    """What each run of check.py printed in the main conversation of the stream's session."""
    record = trying.record.conversation(session_of(stream))
    return [out for _, out in check_outputs(record, repo)]


def check_outputs(record: str, cwd: str) -> list[tuple[str, str]]:
    """Each run of check.py in the records the path or glob pattern names, as the command and what
    it printed."""
    found = [e for path in glob.glob(record) for e in trying.record.read(path) or []]
    return [
        (str(d.given.get("command", "")), d.result)
        for d in trying.record.done(found, cwd)
        if d.tool == "Bash" and "scripts/check.py" in str(d.given.get("command", ""))
    ]


def judged(
    pin: str,
    path: str,
    place: str,
    turns: list[dict[str, Any]],
    wanted: list[tuple[str, bool]] | None = None,
) -> list[str]:
    """What is wrong in the run, from check.py of the copy of pin on the tree at the path, the
    person's view of each message and the judge of the tree, against the intent's points or each
    point wanted; printing what check.py said."""
    return held(pin, path) + wrong_in(turns, judged_tree(path, place, wanted), wanted)


def held(pin: str, path: str) -> list[str]:
    """That the tree at the path does not hold with no decision open, by check.py of the copy of
    pin, where it does not; printing what check.py said."""
    done = checked(pin, path)
    print("  check.py:", done.stdout.strip() or done.stderr.strip())
    if done.returncode != 0 or "No decision is open." not in done.stdout:
        return ["the tree does not hold with no decision open"]
    return []


verdict = trying.verdict
main = trying.main
