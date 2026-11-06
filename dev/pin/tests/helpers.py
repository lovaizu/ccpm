"""What pin's tests stand on beside what every plugin's tests do: pin's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; a small
design tree of the notes app's plan that holds, for each test to change one thing of; and, for an
architecture test, a double of the pinner that writes the tree of each step and runs check.py by
the command pin:down names."""

from __future__ import annotations

import copy
import glob
import json
import os
import re
import subprocess
import sys
from typing import Any

PIN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "pin")
)
DOMAIN = os.path.join(PIN, "core", "domain")
SCRIPTS = os.path.join(PIN, "scripts")
sys.path[:0] = [DOMAIN, SCRIPTS, os.path.join(PIN, "..", "..", "dev", "lane")]

import check
import testing
import tree

__all__ = ["check", "testing", "tree"]

with open(os.path.join(PIN, "README.md"), encoding="utf-8") as f:
    README = f.read()
# The design tree the README's walkthrough shows, as its Markdown.
README_TREE: str = re.search(r"```markdown\n(.*?)```", README, re.DOTALL).group(1)  # type: ignore[union-attr]
# A small design tree of the notes app's plan that holds, for each test to change one thing of: D3
# serves D1, so it stands under D1, and names D1, which it builds on, on its Also line.
WALKTHROUGH_MARKDOWN = """\
# Design tree

Goal: Scripts that read `notes list` get its notes as JSON, so they stop parsing text.
- Grounds: the person, 2026-11-03

- **Q1** Can each script that reads notes list read the JSON as it is?
  - **D1 The form of the JSON**: one JSON array, one object for each note (user)
    - Grounds: the person, 2026-11-03
    - **D3 The form of updated**: ISO 8601, as the text gives it (research)
      - Grounds: scripts/sync.py:14 "datetime.fromisoformat(fields[3])"
      - Grounds: the person confirmed, 2026-11-03
      - Also builds on: D1
- **Q2** Do people who read notes list by eye see the same as before?
  - **D2 Whether text stays the default**: it stays; JSON only with --json (reasoning)
    - Grounds: the goal, and Q2
"""
WALKTHROUGH: dict[str, Any] = tree.read(WALKTHROUGH_MARKDOWN)
# What the tree decides each decision as.
WALKTHROUGH_DECIDED = {d["id"]: d["decided"] for d in WALKTHROUGH["decisions"]}


def walkthrough() -> dict[str, Any]:
    """A copy of the small design tree, for a test to change."""
    return copy.deepcopy(WALKTHROUGH)


def decision(name: str, **given: Any) -> dict[str, Any]:
    """A decision of the ID name, open, serving Q1 and building on none, with each field given
    in its place."""
    made: dict[str, Any] = {
        "id": name,
        "what": f"what {name} decides",
        "contributes_to": ["Q1"],
        "builds_on": [],
        "decided": None,
        "settled_by": None,
        "grounds": [],
    }
    made.update(given)
    return made


def settled(name: str, **given: Any) -> dict[str, Any]:
    """A decision of the ID name, decided by the person, as decision makes it otherwise, with
    each field given in its place."""
    return decision(
        name,
        **{"decided": f"{name} decided", "settled_by": "user", "grounds": ["the person"], **given},
    )


def made(*decisions: dict[str, Any], questions: tuple[str, ...] = ("Q1",)) -> dict[str, Any]:
    """A design tree of the decisions, under a confirmed goal and the questions of the ids."""
    return {
        "goal": {"what": "the goal", "grounds": ["the person"]},
        "questions": [{"id": q, "what": f"does {q} hold?"} for q in questions],
        "decisions": list(decisions),
    }


# The notes app the ux trials work on, kept in ux/notes/ for them too: notes.py prints each
# note as a line of tab-separated fields, and the scripts read that text; sync.py reads `updated`
# as ISO 8601, a fact the pinner finds. Each file by its path in the app.
SUBJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ux", "notes")
NOTES: dict[str, str] = {}
for folder, _, names in os.walk(SUBJECT):
    for name in names:
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            NOTES[os.path.relpath(os.path.join(folder, name), SUBJECT)] = f.read()


def entry(*path: str) -> str:
    """The text of a file of Pin's, at its path in Pin's folder."""
    with open(os.path.join(PIN, *path), encoding="utf-8") as f:
        return f.read()


# The guard's modules, as Pin takes them through its link to Lane's code.
hook, schema, guard, result = testing.lane_code(PIN, "hook", "schema", "guard", "result")
PINNER_PART = entry("core", "roles", "pinner.md")
# The line a Reply begins with, and the line an Answer begins with, as the pinner's part gives them.
FOR_THE_PERSON = "For the person:"
ANSWERED = "The person's answer, word for word:"
assert f"begins with the line `{FOR_THE_PERSON}`" in PINNER_PART
assert f"first line is `{ANSWERED}`" in PINNER_PART
# Pin's Rules laid, as lay.py wrote them.
LAID: dict[str, Any] = json.loads(entry("hooks", "lanes.json"))
# The check command, as the pinner's rule on step 1 names it, of the design tree's path.
(CHECK,) = [
    lane["takes"][0]
    for step in LAID["subagents"][0]["steps"]
    for lane in step["lanes"]
    if (step["step"], lane["lane"]) == (1, "run_only")
]
# Where the person's design tree lies, as the orchestrator picks it for a new plan, and where the
# user's AI of the tests writes its own.
PERSONS = os.path.join(".pin", "20261103-notes-json", "design-tree.md")
AIS = os.path.join(".maker", "notes-json", "design-tree.md")
PINNER = testing.Run("pin:pinner", "p1")
# A decision put to the person, the form of the JSON, as the pinner's part gives a Reply; and the
# fact found that the form of updated rests on, as the pinner quotes it.
FORM = (
    "For the person:\n"
    "Each script is to read the JSON in the form it expects. notes list gives text only, so no"
    " JSON form is set yet (notes.py:18). One JSON array and one object a line serve equally well,"
    " and nothing found favors either.\n"
    "Shall the JSON be one array of all notes, which jq and json.load read whole?"
)
FOUND = 'scripts/sync.py:14 "datetime.fromisoformat(fields[3])"'
# What Pin's guard tells the main conversation, as the routes laid have it: the first start, the
# wait for the pinner, its point to put to the person, and the end of the run; and the sentence a
# start not due is stopped with.
FIRST = "pin: Start `pin:pinner`."
WAIT = "pin: Wait for `pin:pinner` to end: you are told the next start once it has."
ASKED = (
    "pin: pinner gave `asks`. Put its point to the user, and resume `pin:pinner` with their answer"
    " by SendMessage."
)
END = "pin: pinner gave `done`. Start no more subagents."
FOLLOWED = "pin: Start each subagent you are told to start, until you are told to start no more."


def handed(event: dict[str, Any]) -> str:
    """What is wrong with the event as Claude Code hands it, by the guard's own check of the fields
    the hooks reference documents, and an Agent call's tool_response held to what the guard reads
    of it; "" where nothing is. An event of the main conversation has no subagent's fields, so it
    is held with them filled."""
    held = event["hook_event_name"]
    wrong = hook.event_wrong({"agent_id": "main", "agent_type": "", **event}, held)
    if wrong or held != "PostToolUse" or event["tool_name"] != "Agent":
        return wrong
    out = schema.held(guard.BACK, event["tool_response"])
    return out.told() if out is not None else ""


def new(source: dict[str, Any]) -> dict[str, Any]:
    """The tree as the pinner writes it first for a plan: the goal not confirmed, every decision
    open."""
    first = copy.deepcopy(source)
    first["goal"]["grounds"] = []
    for d in first["decisions"]:
        d.update(decided=None, settled_by=None, grounds=[])
    return first


class PinnerTest(testing.FolderTest):
    """A test of a path of Pin's Sequences, in the notes app's repository `repo` in `base`: Pin's
    guard runs real, by Pin's hook entries on Pin's Rules laid, through a double of Claude Code
    working in `repo`, whose hooks keep their records in `base` as the system's temporary folder;
    check.py runs real, by the command the pinner's rule names. Doubles stand in for the
    orchestrator, the main conversation that follows pin:down; for the pinner; and for the user: the
    person, whose answers are set, and, where `called`, the user's AI, which calls the skill with a
    design tree it wrote at `path`."""

    called = False
    path = PERSONS

    def setUp(self) -> None:
        super().setUp()
        self.repo = os.path.join(self.base, "notes")
        for name, text in NOTES.items():
            self.write(os.path.join(self.repo, name), text)
        self.env = {**os.environ, "TMPDIR": self.base}
        self.claude = testing.ClaudeCode(PIN, self.repo, self.env, check=handed)
        self.check = CHECK.replace("${CLAUDE_PLUGIN_ROOT}", PIN).replace("{design}", self.path)
        # What reached the person from the orchestrator, in order.
        self.heard: list[str] = []

    def begins(self) -> list[str]:
        """The run begins: the person types `/pin:down`, or, where `called`, the user's AI calls the
        skill pin:down; what the main conversation is told, which must name the first start."""
        if self.called:
            begun = self.claude.skill("pin:down")
            self.assertTrue(begun.made, begun.said)
            told = begun.context
        else:
            told = self.claude.typed("pin:down")
        self.assertEqual(told[-1:], [FIRST])
        return told

    def on_disk(self) -> dict[str, Any]:
        """The design tree on disk, as tree.py reads it."""
        return tree.load(os.path.join(self.repo, self.path))

    def lies(self, data: dict[str, Any]) -> None:
        """Lays the design tree on disk before the run, as a stopped run or the user's AI left
        it."""
        self.write(os.path.join(self.repo, self.path), tree.markdown(data))

    def picks(self, words: str) -> str:
        """The design tree's path, as the orchestrator picks it for a plan of the person's: the file
        in `.pin/` whose goal holds the words, else a new path there, PERSONS."""
        for path in sorted(glob.glob(os.path.join(self.repo, ".pin", "*", "design-tree.md"))):
            if words in tree.load(path)["goal"]["what"]:
                return os.path.relpath(path, self.repo)
        return PERSONS

    def starts(self, request: str) -> testing.Told:
        """The run begins, as `begins` says, and the orchestrator starts the pinner, the start due,
        with the Request: the design tree's path as one JSON object on its first line, then the
        request; fails the test where the start is not made, the pinner is not given its part whole
        as it starts, or the main conversation is not told to wait for it. The orchestrator then
        ends its turn, which goes."""
        self.begins()
        prompt = json.dumps({"design": self.path}) + "\n" + request
        told = self.claude.start(None, PINNER, prompt)
        self.assertTrue(told.made, told.said)
        part = PINNER_PART.replace("${CLAUDE_PLUGIN_ROOT}", PIN)
        self.assertTrue(any(part in said for said in told.context), told.context)
        self.assertEqual(told.context[-1], WAIT)
        self.assertTrue(self.claude.end_turn().made)
        return told

    def writes(self, data: dict[str, Any], path: str = "") -> testing.Told:
        """The pinner writes the data, at the design tree's path or the path given: only a tree in
        the form check.py's unit tests hold it to, as the pinner's contract allows. It makes a file
        not yet there with Write, and changes one there with Edit after reading it, its whole text
        the old string, as the pinner's part allows; the Edit's Told."""
        self.assertEqual(tree.form_faults(data), [])
        file = os.path.join(self.repo, path or self.path)
        if not os.path.exists(file):
            return self.claude.call(
                PINNER, "Write", {"file_path": file, "content": tree.markdown(data)}
            )
        self.assertTrue(self.claude.call(PINNER, "Read", {"file_path": file}).made)
        with open(file, encoding="utf-8") as f:
            now = f.read()
        given = {"file_path": file, "old_string": now, "new_string": tree.markdown(data)}
        return self.claude.call(PINNER, "Edit", given)

    def rewrites(self, data: dict[str, Any]) -> testing.Told:
        """The pinner writes the design tree, there already, whole with Write, which its part does
        not allow."""
        file = os.path.join(self.repo, self.path)
        return self.claude.call(
            PINNER, "Write", {"file_path": file, "content": tree.markdown(data)}
        )

    def reads(self, path: str) -> testing.Told:
        """The pinner reads a file of the repository with Read."""
        return self.claude.call(PINNER, "Read", {"file_path": os.path.join(self.repo, path)})

    def runs(self, command: str) -> testing.Told:
        """The pinner runs the command with Bash."""
        return self.claude.call(PINNER, "Bash", {"command": command, "description": "d"})

    def checks(self) -> tuple[int, str]:
        """The pinner runs the check by its rule's command, which goes through; the Check result,
        the exit code and what check.py printed, as the run gave them."""
        told = self.runs(self.check)
        self.assertTrue(told.made, told.said)
        done = subprocess.run(
            ["sh", "-c", self.check], capture_output=True, text=True, cwd=self.repo, check=False
        )
        return done.returncode, done.stdout + done.stderr

    def gives(self, on: str) -> testing.Told:
        """The pinner gives its result by the command its last step names: only a result Pin's
        result script takes, as the pinner's contract allows."""
        self.assertEqual(result.said(["pinner", on], PIN), "")
        return self.runs(f"python3 {PIN}/hooks/lane/result.py pinner {on}")

    def ends(self, reply: str, told: str = ASKED) -> str:
        """The pinner ends with the Reply, which must be in the form the pinner's part gives, and is
        let end; its end reaches the main conversation, which must be told the line given; the
        orchestrator puts the Reply to the person as given, and ends its turn, which goes: what the
        person heard."""
        self.assertTrue(reply.startswith(FOR_THE_PERSON + "\n"), reply)
        ended = self.claude.stop(PINNER)
        self.assertTrue(ended.made, ended.said)
        self.assertEqual(self.claude.notify(PINNER), [told])
        heard = reply[len(FOR_THE_PERSON) + 1 :]
        self.heard.append(heard)
        turn = self.claude.end_turn()
        self.assertEqual((turn.made, turn.said), (True, {}))
        return heard

    def answers(self, words: str) -> None:
        """The person answers, which the main conversation is told to put back to the pinner; the
        orchestrator resumes the pinner by SendMessage with their words, word for word, under the
        Answer's line, which goes through, and Claude Code starts the pinner again."""
        self.assertEqual(self.claude.prompted(words), [ASKED])
        message = {"to": PINNER.agent_id, "message": f"{ANSWERED}\n{words}"}
        sent = self.claude.call(None, "SendMessage", message)
        self.assertEqual((sent.made, sent.said), (True, {}))
        self.claude.started(PINNER)

    def holds(self, *open_now: str) -> tuple[int, str]:
        """The Check result where the design tree holds, with the decisions open now."""
        said = f"Open to decide now: {', '.join(open_now)}." if open_now else "No decision is open."
        return 0, f"check.py: {self.path} holds: {check.HOLDS}\n{said}\n"

    def hands_back(self) -> testing.Told:
        """The orchestrator gives `done` for the design handed back, by the command its last step
        names, run in the main conversation."""
        command = f"python3 {PIN}/hooks/lane/result.py down done"
        return self.claude.call(None, "Bash", {"command": command, "description": "d"})
