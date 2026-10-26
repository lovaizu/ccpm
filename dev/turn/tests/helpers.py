"""What turn's tests share: a temporary folder standing for the user's repository, holding a task's
CCS, its checklist, its decisions and a work already written, turn run on it as the orchestrator
runs it, and the replies and checks of a run, each written once here."""

import contextlib
import io
import json
import os
import re
import sys
import time
from unittest import mock

TURN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
)
SCRIPTS = os.path.join(TURN, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(TURN, "..", "dev", "lane"))

import call  # noqa: F401  (each of turn's modules, for its own tests)
import forms  # noqa: F401
import prompts  # noqa: F401
import run
import state
import testing

import turn

# The wait for a messaged role's reply as turn has it, before each test sets its own.
WAITED = run.WAIT

# The items of the run's checklist, by its path and ID.
ITEM_F1 = {"checklist": "checklists/readme.md", "item": "F-1"}
ITEM_B1 = {"checklist": "checklists/readme.md", "item": "B-1"}
ITEMS = [ITEM_F1, ITEM_B1]
CHECKLIST = """---
name: readme
version: 0.1.0
---

# README

A README is read by whoever meets the project first.

## Format

### F-1: Shape

Scope: whole

Does the README follow this template?

## Benefit

### B-1: Who it is for

Scope: its part

On opening it, can the reader tell whether the project is for them?
"""
CCS = {
    "focal_entities": [{"deliverable": "README.md"}, {"audience": "a developer new to it"}],
    "goal_orientation": [{"purpose": "to try it on their own files"}],
    "retrieved_artifacts": [
        {"checklist": "checklists/readme.md"},
        {"decisions": "notes/readme.decisions.md"},
        {"page": "docs/start.md"},
    ],
}
CALL = {
    "ccs": ".tasks/readme.json",
    "kind": {
        "work": "deliverable",
        "checklist": "checklist",
        "receiver": "audience",
        "use": "purpose",
        "has": "page",
    },
    "result": ".tasks/readme-result.json",
    "test": "sh tests/readme.sh",
}
GOOD = {
    "checklist": "checklists/readme.md",
    "item": "F-1",
    "good": "the reader finds each part where a README keeps it",
    "lines": ["README.md:1-3"],
}
# The generator's claim of every item's Good, naming no choice of its own.
CLAIM = {"items": [GOOD, dict(GOOD, item="B-1")], "questions": [], "chosen": []}
# A choice the work rests on that the CCS leaves open, as the generator names it.
CHOSEN = {"chosen": "the example tidies people.csv", "why": "no decision names a file"}
WAITS = {"checklist": "checklists/readme.md", "item": "B-1", "question": 1}
QUESTION = {"question": "Under which license may people use it?", "recommended": "MIT"}
# The question an item waits on, as the calling AI is sent it, and the answer kept for it.
ASKED = {"questions": [dict(QUESTION, items=[ITEM_B1])]}
ANSWER = dict(ASKED, answer="MIT")
# The first user's Good for each item.
FOUND = {
    "checklist": "checklists/readme.md",
    "item": "F-1",
    "good": "the name, then what it does, as READMEs open",
    "lines": ["README.md:1-3"],
}
FOUND_B1 = dict(FOUND, item="B-1")
# The orchestrator's check before the work is made: what in the CCS and its files gives each item's
# Good.
CAN = [
    {"checklist": "checklists/readme.md", "item": "F-1", "can": "the template the checklist gives"},
    {"checklist": "checklists/readme.md", "item": "B-1", "can": "the receiver the CCS names"},
]
# An item the first user finds no Good for, with the places of the work where it looked for it, what
# it did there and what it did not get.
DID = "read the opening for whom it is"
LACKING = "whether it is for a developer"


def stopped(item):
    """The first user's stop at the item: where it looked for its Good, what it did there and what
    it did not get."""
    return dict(item, places=["README.md:1-1"], did=DID, lacking=LACKING)


STOPPED_F1 = stopped(ITEM_F1)
STOPPED_B1 = stopped(ITEM_B1)
# A first user's reading of every item: the Good it found for one, and where it stopped at the
# other.
FIRST_READ = [FOUND, STOPPED_B1]
# A checklist item asked of each part of the work, added to a run's checklist where a test needs
# one; the work's parts, as the script splits a README of a title, an opening and one section;
# and a Good for each.
EACH = """
### B-2: Each part used

Scope: each part

Does the reader use each part toward their purpose?
"""
EACH_ITEM = {"checklist": "checklists/readme.md", "item": "B-2"}
SECTIONED = "# csvtidy\n\nTidies CSV files.\n\n## Use\n\nRun it.\n"
EACH_GOOD = {
    "checklist": "checklists/readme.md",
    "item": "B-2",
    "parts": [
        {"part": "README.md:1-4", "good": "the reader learns what it is", "lines": ["README.md:3"]},
        {
            "part": "README.md:5-7",
            "good": "the reader learns how to run it",
            "lines": ["README.md:7"],
        },
    ],
}


# The agent ID the Agent call gives back for each role, as the orchestrator hands it on.
IDS = {"turn:generator": "agen", "turn:first-user": "afirst"}
RESULT = CALL["result"]
# The day a run is started on, as the clock gives it, and the folder the run of the result is kept
# in, in turn's folder at the root of the repository, named by that day and the result's path from
# the root, each `/` written `%2F`.
TODAY = "20261025"
RUN = f".turn/{TODAY}-.tasks%2Freadme-result.json"


class RepoTest(testing.FolderTest):
    """Each test runs turn from a temporary folder standing for the user's repository, `base`, its
    root, holding a task's CCS, its checklist, its decisions and a work already written, on the
    day TODAY."""

    def setUp(self):
        super().setUp()
        os.mkdir(".git")
        today = mock.patch.object(time, "strftime", return_value=TODAY)
        today.start()
        self.addCleanup(today.stop)
        self.write_json(CALL["ccs"], CCS)
        self.write("checklists/readme.md", CHECKLIST)
        self.write("notes/readme.decisions.md", "# Decisions\n")
        self.write("docs/start.md", "# Start\n")
        self.write("README.md", "# csvtidy\n\nTidies CSV files.\n")
        self.result = RESULT
        # A role's reply is written by the time the flow reads it, unless a test says otherwise.
        self.waiting = mock.patch.object(run, "WAIT", 0)
        self.waiting.start()
        self.addCleanup(self.waiting.stop)

    def turn(self, *argv, stdin=""):
        """What turn.py gives back and prints, run with the arguments and the standard input."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = turn.main(list(argv), io.StringIO(stdin))
        return code, out.getvalue()

    def state(self):
        """Where the run stands, as its state keeps it."""
        return self.read_json(state.state_path(self.result))

    def printed(self, out):
        """What the script printed: a move as the line it tells, where it has one, and the tool
        call itself; anything else as its JSON."""
        lines = out.rstrip("\n").split("\n")
        try:
            move = json.loads(lines[-1])
        except ValueError:
            move = None
        if isinstance(move, dict) and set(move) == {"tool", "input"}:
            return {"line": lines[0], "move": move} if lines[1:] else {"move": move}
        return json.loads(out)

    def next(self, given=None):
        """What the script prints next for the run, handed the orchestrator's check, its questions
        or the agent ID, as JSON."""
        stdin = json.dumps(given) if given is not None else ""
        code, out = self.turn("next", self.result, stdin=stdin)
        self.assertEqual(code, 0, out)
        head, _, page = out.partition("\n")
        count = re.match(r"\w+, page 1 of (\d+): ", head)
        if count is None:
            return self.printed(out)
        # A print too long for one read comes in pages, each without its head and the line end
        # print adds.
        for n in range(2, int(count.group(1)) + 1):
            page = page[:-1] + self.turn("next", self.result, str(n))[1].partition("\n")[2]
        return json.loads(page)

    def laid_out_anew(self):
        """The calling AI keeps in the CCS an answer that adds a file to the work, LICENSE."""
        ccs = self.read_json(CALL["ccs"])
        ccs["focal_entities"].append({"deliverable": "LICENSE"})
        self.write_json(CALL["ccs"], ccs)

    def answered(self, answer="MIT"):
        """What the script prints once the calling AI's answer, handed on as it came, is given."""
        code, out = self.turn("next", self.result, stdin=answer)
        self.assertEqual(code, 0, out)
        return self.printed(out)

    def refused(self, given=None):
        """What the script prints when it refuses to go on with the run."""
        stdin = given if isinstance(given, str) else json.dumps(given) if given else ""
        code, out = self.turn("next", self.result, stdin=stdin)
        self.assertEqual(code, 1, out)
        return out

    def heard(self, out):
        """What the script prints after the line telling the calling AI, which the orchestrator
        sends to `main` first."""
        self.assertEqual(out["move"]["tool"], "SendMessage", out)
        self.assertEqual(out["move"]["input"]["to"], "main")
        return self.next()

    def due(self, out):
        """The role's move after the line telling the calling AI: the Agent call starting the role,
        or the message sent to it."""
        return self.heard(out)["move"]

    def here(self, path):
        """The path as a whole path in the folder the call was made from, as a role is given it."""
        return os.path.join(self.base, path)

    def kept(self, name):
        """The whole path of the file of the name in the folder the run of RESULT is kept in."""
        return self.here(f"{RUN}/{name}")

    def prompt(self):
        """What the role due is given, as its prompt holds it."""
        return self.state()["next"]["prompt"]

    def started(self, asked=None):
        """The run started on a call, by default the run's, and checked to give every item its
        Good; and the move starting the generator."""
        asked = asked or CALL
        self.result = str(asked["result"])
        code, out = self.turn("start", json.dumps(asked))
        self.assertEqual(code, 0, out)
        return self.due(self.next({"items": CAN, "questions": []}))

    def replied(self, reply):
        """The role due writes its reply, and the orchestrator goes on with the agent ID the Agent
        call gave back where it started the role; what the script prints then."""
        step = self.state()["next"]
        self.write(step["prompt"]["reply"], reply if isinstance(reply, str) else json.dumps(reply))
        given = None if "to" in step or "id" in step else {"agent_id": IDS[step["agent"]]}
        return self.next(given)

    def made(self, *claim, chosen=()):
        """The generator due replies with its claim, by default every item Good, naming the choices
        given; and what the script prints then."""
        claim = claim or tuple(CLAIM["items"])
        asks = [QUESTION] if any("question" in i for i in claim) else []
        return self.replied({"items": list(claim), "questions": asks, "chosen": list(chosen)})

    def reading(self, *found):
        """A first user's reading giving the Goods found, and every other item the places it looked
        for its Good, what it did there and what it did not get."""
        given = {(i["checklist"], i["item"]) for i in found}
        return list(found) + [
            stopped(i) for i in self.state()["items"] if (i["checklist"], i["item"]) not in given
        ]

    def first_read(self, *found, claim=(), claim_chosen=()):
        """The round taken through the generator's claim, naming the choices given, and the first
        user's reading giving the Goods found, the round sending the work back no more; and what
        the script prints then."""
        made = self.made(*claim, chosen=claim_chosen)
        self.assertEqual(self.due(made)["input"]["subagent_type"], "turn:first-user")
        with mock.patch.object(run, "SENDS", 0):
            return self.replied({"items": self.reading(*found)})

    def returned(self, out):
        """The return of the result told as the script printed it, once every item has its Good;
        and what the script prints after the line."""
        self.assertIn("Next, turn:up will return the result", out["line"])
        return self.heard(out)


class ReadTest(RepoTest):
    """A run started and checked to give every item its Good, its generator due."""

    def setUp(self):
        super().setUp()
        self.started()
