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
FINDS = """You stand in for the person a planning AI is talking with. Here is who you are and what
you truly want; the AI cannot see it:

{intent}

The conversation so far, oldest first:

{said}

The AI's newest message to you:

<message>
{message}
</message>

Answer it as that person would. Also judge the message as that person, from what you know. Give
only one JSON object, with no other text, with these keys:
- "answer": your answer to the message, as you would write it;
- "points": how many separate things the message asks you to decide or to confirm, as a number;
- "asks_fact": true where the message asks you something about the repository that the AI could
  read for itself, rather than showing you what it found for you to confirm; otherwise false;
- "asks_settled": true where it asks you again something you are said, above, to have settled
  already, or something you already answered in this conversation; otherwise false;
- "confirms_design": true where it shows you the whole design and asks whether you understand it
  the same way; otherwise false;
- "finished": true where the message asks you nothing and says the planning is done; otherwise
  false."""
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


def asked(prompt: str, cwd: str) -> dict[str, Any]:
    """The JSON object an AI gives for the prompt, on Opus, with no tool, no plugin and no record
    kept, run in the folder given, which holds nothing of pin's."""
    command = ["claude", "-p", "--model", "opus", "--tools", "", "--no-session-persistence"]
    command += ["--output-format", "json", "--settings", json.dumps({"enabledPlugins": {}})]
    done = subprocess.run(
        command, input=prompt, capture_output=True, text=True, cwd=cwd, timeout=300, check=True
    )
    said = str(json.loads(done.stdout)["result"])
    found = re.search(r"\{.*\}", said, re.DOTALL)
    if not found:
        raise SystemExit(f"the stand-in gave no JSON: {said}")
    return json.loads(found.group(0))


def made(place: str, plugins: dict[str, str]) -> tuple[str, dict[str, str]]:
    """The repository of the run, `notes` in its folder, with the notes app committed, and a copy
    of pin and of each plugin given by its folder beside it, by name; gives the repository and the
    copies' folders, pin's under "pin"."""
    repo = os.path.join(place, "notes")
    for path, text in NOTES.items():
        os.makedirs(os.path.dirname(os.path.join(repo, path)), exist_ok=True)
        with open(os.path.join(repo, path), "w", encoding="utf-8") as f:
            f.write(text)
    for args in (["init", "-q", "-b", "main"], ["add", "."]):
        subprocess.run(["git", "-C", repo, *args], check=True)
    who = ["-c", "user.name=e2e", "-c", "user.email=e2e@example.com"]
    subprocess.run(["git", "-C", repo, *who, "commit", "-q", "-m", "notes"], check=True)
    copies = {}
    for name, source in {"pin": PIN, **plugins}.items():
        copies[name] = os.path.join(place, "plugins", name)
        shutil.copytree(source, copies[name])
    return repo, copies


def talked(
    conversation: trying.Conversation, first: str, place: str, stream: str, intent: str = INTENT
) -> list[dict[str, Any]]:
    """Each message the AI put to the person, with what the person said of it, from the first
    message sent until the person has confirmed the design and the AI has replied, or the AI says it
    is done; the person answers from the intent, in a folder of its own in the run's folder."""
    alone = os.path.join(place, "person")
    os.makedirs(alone)
    said: list[str] = []
    turns: list[dict[str, Any]] = []
    reply = conversation.send(first, stream, idle=True)
    for _ in range(TURNS):
        message = str(reply.get("result", ""))
        heard = asked(
            FINDS.format(intent=intent, said="\n\n".join(said) or "(none)", message=message),
            alone,
        )
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
    raise SystemExit(f"the conversation did not end in {TURNS} messages")


def session_of(stream: str) -> str:
    """The session's ID, from the first line of the stream Claude Code printed."""
    with open(stream, encoding="utf-8") as f:
        return json.loads(f.readline())["session_id"]


def heard_of(heard: dict[str, Any]) -> str:
    """What the person said of a message, in a few words."""
    keys = ("points", "asks_fact", "asks_settled", "confirms_design", "finished")
    return " ".join(f"{k}={heard.get(k)}" for k in keys)


def checked(pin: str, path: str) -> subprocess.CompletedProcess:
    """check.py of the copy of pin run on the tree at the path."""
    command = [sys.executable, os.path.join(pin, "scripts", "check.py"), path]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def judged_tree(path: str, place: str) -> list[dict[str, Any]]:
    """For each of the intent's points, whether the tree at the path holds it and who settled it,
    as an AI judges it given the points and the tree."""
    with open(path, encoding="utf-8") as f:
        tree = f.read()
    wants = "\n".join(f"{n}. {w}" for n, (w, _) in enumerate(WANTS, 1))
    return asked(JUDGES.format(wants=wants, tree=tree), os.path.join(place, "person"))["points"]


def wrong_in(turns: list[dict[str, Any]], points: list[dict[str, Any]]) -> list[str]:
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
    for p, (want, theirs) in zip(points, WANTS):
        if not p.get("held"):
            wrong.append(f"the tree does not hold: {want}")
        elif theirs and p.get("settled_by") != "user":
            wrong.append(f"settled without the person: {want} ({p.get('settled_by')})")
    return wrong


def tried_in(tree: dict[str, Any], outputs: list[str]) -> list[str]:
    """Which invited break the run did not meet: a fact of the repository settling a decision, and
    more than one decision open to decide at once, from the tree and check.py's outputs."""
    untried = []
    if not any(
        d.get("settled_by") == "research" and "scripts/" in " ".join(d.get("grounds", []))
        for d in tree.get("decisions", [])
    ):
        untried.append("no decision was settled by a fact found in scripts/")
    if not any(re.search(r"Open to decide now: \S+, ", out) for out in outputs):
        untried.append("check.py never named more than one decision open at once")
    return untried


def check_outputs(record: str, cwd: str) -> list[tuple[str, str]]:
    """Each run of check.py in the records the path or glob pattern names, as the command and what
    it printed."""
    found = [e for path in glob.glob(record) for e in trying.record.read(path) or []]
    return [
        (str(d.given.get("command", "")), d.result)
        for d in trying.record.done(found, cwd)
        if d.tool == "Bash" and "scripts/check.py" in str(d.given.get("command", ""))
    ]


def main(run: Any) -> None:
    """Runs the E2E test's run as many times as the command line gives, three by default, numbered
    from the second word where given, and exits 0 where every run passed and counted."""
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    passed = [run(n) for n in range(first, first + runs)]
    print(f"{sum(passed)} of {runs} runs passed")
    sys.exit(0 if all(passed) else 1)
