import contextlib
import io
import json
import os
import re
import sys
from unittest import mock

TURN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
)
SCRIPTS = os.path.join(TURN, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(TURN, "..", "dev", "lane"))

import forms  # noqa: F401  (the forms, for their own tests)
import records  # noqa: F401  (the records, for their own tests)
import run
import testing

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
}
GOOD = {
    "checklist": "checklists/readme.md",
    "item": "F-1",
    "good": "the reader finds each part where a README keeps it",
    "lines": ["README.md:1-3"],
}
WAITS = {"checklist": "checklists/readme.md", "item": "B-1", "question": 1}
QUESTION = {"question": "Under which license may people use it?", "recommended": "MIT"}
FOUND = {
    "checklist": "checklists/readme.md",
    "item": "F-1",
    "good": "the name, then what it does, as READMEs open",
    "lines": ["README.md:1-3"],
}
EVALUATED = {
    "checklist": "checklists/readme.md",
    "item": "F-1",
    "good": "the reader meets the name and what it does first",
    "lines": ["README.md:1-3"],
}
# The orchestrator's check before the work is made: what in the CCS and its files gives each item's
# Good.
CAN = [
    {"checklist": "checklists/readme.md", "item": "F-1", "can": "the template the checklist gives"},
    {"checklist": "checklists/readme.md", "item": "B-1", "can": "the receiver the CCS names"},
]
# A lesson on how the run went, for the generator, resting on words of the first record, which
# every role's record holds.
LESSON = {
    "role": "generator",
    "lesson": "it opened each file before it wrote",
    "grounds": [{"record": 1, "quote": "I open it."}],
}
CHECKED = "every page of every record"
SENT_BACK = {
    "checklist": "checklists/readme.md",
    "item": "B-1",
    "gets": "the reader sees at once that it is for CSV files",
    "places": ["README.md:3-3"],
}
# An item the first user finds no Good for, with the places of the work where it looked for it, what
# it did there and what it did not get.
DID = "read the opening for whom it is"
LACKING = "whether it is for a developer"
STOPPED = {
    "checklist": "checklists/readme.md",
    "item": "B-1",
    "places": ["README.md:3-3"],
    "did": DID,
    "lacking": LACKING,
}
# A first user's reading of every item: the Good it found for one, and where it stopped at the other.
FIRST_READ = [FOUND, STOPPED]
# A checklist item asked of each part of the work, added to a run's checklist where a test needs
# one; the work's parts, as the script splits a README of a title, an opening and one section;
# and a Good for each.
EACH = """
### B-2: Each part used

Scope: each part

Does the reader use each part toward their purpose?
"""
SECTIONED = "# csvtidy\n\nTidies CSV files.\n\n## Use\n\nRun it.\n"
PARTS = ["README.md:1-4", "README.md:5-7"]
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
IDS = {
    "turn:generator": "agen",
    "turn:first-user": "afirst",
    "turn:evaluator": "aeval",
    "turn:learner": "alearn",
}
RESULT = CALL["result"]


class RepoTest(testing.FolderTest):
    """Each test runs turn from a temporary folder standing for the user's repository, holding a
    task's CCS, its checklist, its decisions and a work already written; Claude Code's records are
    kept in a folder of its own inside it."""

    def setUp(self):
        super().setUp()
        self.repo = self.base
        self.write_json(CALL["ccs"], CCS)
        self.write("checklists/readme.md", CHECKLIST)
        self.write("notes/readme.decisions.md", "# Decisions\n")
        self.write("docs/start.md", "# Start\n")
        self.write("README.md", "# csvtidy\n\nTidies CSV files.\n")
        self.result = RESULT
        self.claude = os.path.join(self.repo, ".claude-home")
        self.session = os.path.join(self.claude, "projects", "repo", "s1", "subagents")
        patched = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.claude})
        patched.start()
        self.addCleanup(patched.stop)
        # A role's reply is written by the time the flow reads it, unless a test says otherwise.
        self.waiting = mock.patch.object(run, "WAIT", 0)
        self.waiting.start()
        self.addCleanup(self.waiting.stop)

    def turn(self, *argv, stdin=""):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run.main(list(argv), io.StringIO(stdin))
        return code, out.getvalue()

    def state(self):
        return self.read_json(run.state_path(self.result))

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
        """What the script prints next for the run, handed the orchestrator's check, decision,
        take or agent ID."""
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
        return os.path.join(self.repo, path)

    def prompt(self):
        """What the role due is given, as its prompt holds it."""
        return self.state()["next"]["prompt"]

    def started(self, call=None):
        """The run started on a call and checked to give every item its Good; and the move starting
        the generator."""
        call = call or CALL
        self.result = str(call["result"])
        code, out = self.turn("start", json.dumps(call))
        self.assertEqual(code, 0, out)
        return self.due(self.next({"items": CAN, "questions": []}))

    def replied(self, reply):
        """The role due writes its reply, and the orchestrator goes on with the agent ID the Agent
        call gave back where it started the role; what the script prints then."""
        step = self.state()["next"]
        self.write(step["prompt"]["reply"], reply if isinstance(reply, str) else json.dumps(reply))
        given = None if "to" in step or "id" in step else {"agent_id": IDS[step["agent"]]}
        return self.next(given)

    def made(self, *claim):
        """The generator due replies with its claim, by default every item Good; and what the
        script prints then."""
        claim = claim or (GOOD, dict(GOOD, item="B-1"))
        asks = [QUESTION] if any("question" in i for i in claim) else []
        return self.replied({"items": list(claim), "questions": asks})

    def reading(self, *found):
        """A first user's reading giving the Goods found, and every other item the places it looked
        for its Good, what it did there and what it did not get."""
        given = {(i["checklist"], i["item"]) for i in found}
        return list(found) + [
            dict(i, places=["README.md:1-1"], did=DID, lacking=LACKING)
            for i in self.state()["items"]
            if (i["checklist"], i["item"]) not in given
        ]

    def through(self, *evaluated, claim=(GOOD, WAITS), found=(FOUND,)):
        """The run taken through the generator's claim, the first user's reading, after the round
        has sent it back as often as it may, and the evaluator's Goods; and what the script prints
        then."""
        self.due(self.made(*claim))
        kept = self.state()
        kept["sent"] = run.SENDS
        self.write_json(run.state_path(self.result), kept)
        out = self.replied({"items": self.reading(*found)})
        self.assertEqual(self.due(out)["input"]["subagent_type"], "turn:evaluator")
        return self.replied({"items": list(evaluated)})

    def learnt(self, out, reply=None, taken=None):
        """The learner told and started as the script printed, replying with what it found, by
        default no lesson on the run; then what the orchestrator takes, by default every lesson
        offered; and what the script prints after the line telling it."""
        self.assertEqual(self.due(out)["input"]["subagent_type"], "turn:learner")
        out = self.heard(self.replied(reply or {"process": [], "checked": CHECKED}))
        if "take" in out:
            every = list(range(1, len(out["take"]["process"]) + 1))
            out = self.heard(self.next(taken or {"process": every}))
        return out

    def given_record(self, agent_id, prompt, agent_type="", folder=None):
        """Writes what Claude Code keeps of an agent's conversation: its prompt as the first
        record, then what it said, kept twice as Claude Code keeps it, and its meta file."""
        folder = folder or self.session
        path = os.path.join(folder, f"agent-{agent_id}.jsonl")
        said = {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "I open it."}]},
        }
        entries = [{"type": "user", "message": {"role": "user", "content": prompt}}, said, said]
        self.write(path, "".join(json.dumps(r) + "\n" for r in entries))
        self.write_json(
            os.path.join(folder, f"agent-{agent_id}.meta.json"), {"agentType": agent_type}
        )
        return path
