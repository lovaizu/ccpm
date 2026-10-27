"""What turn's tests share: a temporary folder standing for the user's repository, holding a task's
CCS, its checklist, its decisions and a work already written, turn run on it as the orchestrator
runs it, and the replies and checks of a run, each written once here."""

import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
from unittest import mock

TURN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "turn")
)
SCRIPTS = os.path.join(TURN, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(TURN, "..", "..", "dev", "lane"))

import call  # noqa: F401  (each of turn's modules, for its own tests)
import flow
import forms  # noqa: F401
import items as checklist_items  # noqa: F401
import parts as work_parts  # noqa: F401
import prompts  # noqa: F401
import state
import testing
import turn

# The wait for a messaged role's reply as turn has it, before each test sets its own.
WAITED = flow.WAIT

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
# An item the generator claims passes, with its evidence: the command it ran and what it printed.
PASSED = {
    "checklist": "checklists/readme.md",
    "item": "F-1",
    "evidence": "cat -n README.md: the name on line 1, then what it does on line 3",
}
# The generator's claim of every item passing, naming no choice of its own.
CLAIM = {"items": [PASSED, dict(PASSED, item="B-1")], "questions": [], "chosen": []}
# What a role that stops for what lies outside the work gives: what it tried, what it confirmed and
# what not, and what it needs.
BLOCKED = {
    "tried": "sh tests/readme.sh",
    "confirmed": "README.md is written",
    "not_confirmed": "whether its commands run, as sh tests/readme.sh printed `csvtidy: not found`",
    "needs": "csvtidy installed, as the README's commands run it",
}
# Why the generator holds a gap sent back lies outside the purpose.
OUTSIDE = "the developer tries it on their own files whoever it is for"
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
# An item the first user finds no Good for, with the places of the work where it looked for it, what
# it did there and what it did not get.
DID = "read the opening for whom it is"
LACKING = "whether it is for a developer"
HINDERS = "the developer cannot tell whether to try it"


def stopped(item):
    """The first user's stop at the item: where it looked for its Good, what it did there, what it
    did not get and how that keeps the receiver from using the work."""
    return dict(item, places=["README.md:1-1"], did=DID, lacking=LACKING, hinders=HINDERS)


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
# The entries of a role's record, as Claude Code writes them: a message another session sent it,
# turn:up's; its reply ending its turn; and a stop hook keeping it going.
MESSAGE = {
    "type": "user",
    "message": {"role": "user", "content": "Another Claude session sent a message"},
    "origin": {"kind": "peer", "body": "{}"},
}
END = {
    "type": "assistant",
    "message": {
        "role": "assistant",
        "content": [{"type": "text", "text": "Written."}],
        "stop_reason": "end_turn",
    },
}
HOOK = {"type": "user", "message": {"role": "user", "content": "Stop hook feedback: go on"}}
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
        # Claude Code's records, each role's among them, in a folder of their own beside the
        # repository, as Claude Code keeps them out of it.
        self.config = os.path.realpath(tempfile.mkdtemp(dir=self.run_folder))
        self.addCleanup(shutil.rmtree, self.config)
        config = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.config})
        config.start()
        self.addCleanup(config.stop)
        # A role's reply is written by the time the flow reads it, unless a test says otherwise.
        self.waiting = mock.patch.object(flow, "WAIT", 0)
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
        """What the script printed: the line for the user, where it has one, then a move as the tool
        call itself, or anything else as its JSON."""
        line, rest = self.told(out)
        found = json.loads(rest)
        printed = {"move": found} if set(found) == {"tool", "input"} else found
        return dict(printed, line=line) if line else printed

    def told(self, out):
        """The line for the user the script printed first, or "" where it printed none, and what it
        printed after."""
        head, _, rest = out.partition("\n")
        return (head, rest) if head.startswith("turn: ") and rest else ("", out)

    def next(self, given=None):
        """What the script prints next for the run, handed the orchestrator's questions or the
        agent ID, as JSON."""
        stdin = json.dumps(given) if given is not None else ""
        code, out = self.turn("next", self.result, stdin=stdin)
        self.assertEqual(code, 0, out)
        line, rest = self.told(out)
        head, _, page = rest.partition("\n")
        count = re.match(r"\w+, page 1 of (\d+): ", head)
        if count is None:
            return self.printed(out)
        # A print too long for one read comes in pages, each without its head and the line end
        # print adds.
        for n in range(2, int(count.group(1)) + 1):
            page = page[:-1] + self.turn("next", self.result, str(n))[1].partition("\n")[2]
        found = json.loads(page)
        return dict(found, line=line) if line else found

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
        """What the orchestrator takes once the line for the user is sent: where the line is a move
        of its own, sent to `main` before a role is started, what the script prints next; otherwise
        what came with the line."""
        move = out.get("move", {})
        if move.get("tool") == "SendMessage" and move["input"]["to"] == "main":
            return self.next()
        return {k: v for k, v in out.items() if k != "line"}

    def line_of(self, out):
        """The line for the user the script printed, with a move or as the message of a move of its
        own sent to `main`."""
        return out.get("line") or out["move"]["input"]["message"]

    def due(self, out):
        """The role's move once the line for the user is sent: the Agent call starting the role, or
        the message sent to it."""
        return self.heard(out)["move"]

    def here(self, path):
        """The path as a whole path in the folder the call was made from, as a role is given it."""
        return os.path.join(self.base, path)

    def files(self, agent, *more):
        """The files of the run a role is given, as the CCS of the tests names them, each a whole
        path, with each file of the work given more: what it reads, the generator the CCS and every
        file it names, the first user what the receiver has with the work; the work, the checklists,
        and where it replies."""
        work = [self.here(p) for p in ("README.md", *more)]
        checklist = [self.here("checklists/readme.md")]
        if agent == "turn:generator":
            named = ["notes/readme.decisions.md", "docs/start.md"]
            read = [self.here(CALL["ccs"]), *work, *checklist, *(self.here(p) for p in named)]
        else:
            read = [*work, self.here("docs/start.md"), *checklist]
        reply = self.kept(f"{agent.partition(':')[2]}.json")
        return {"given": read, "work": work, "checklists": checklist, "reply": reply}

    def kept(self, name):
        """The whole path of the file of the name in the folder the run of RESULT is kept in."""
        return self.here(f"{RUN}/{name}")

    def prompt(self):
        """What the role due is given, as its prompt holds it."""
        return self.state()["next"]["prompt"]

    def started(self, asked=None):
        """The run started on a call, by default the run's; and the move starting the generator."""
        asked = asked or CALL
        self.result = str(asked["result"])
        code, out = self.turn("start", json.dumps(asked))
        self.assertEqual(code, 0, out)
        return self.due(self.next())

    def replied(self, reply):
        """The role due writes its reply and ends, its record then holding the message it was
        started or sent and the reply ending its turn, and the orchestrator goes on with the agent
        ID the Agent call gave back where it started the role, or with nothing where the role was
        sent a message; what the script prints then."""
        step = self.state()["next"]
        self.write(step["prompt"]["reply"], reply if isinstance(reply, str) else json.dumps(reply))
        self.recorded(step.get("to") or step.get("id") or IDS[step["agent"]], MESSAGE, END)
        if "to" in step or "id" in step:
            return self.next()
        return self.next({"agent_id": IDS[step["agent"]]})

    def recorded(self, agent, *entries):
        """Adds the entries to the record Claude Code keeps of the agent of the ID, beside the
        record of the conversation that started turn:up."""
        path = os.path.join(self.config, "projects", "-repo", "session", "subagents")
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, f"agent-{agent}.jsonl"), "a", encoding="utf-8") as f:
            f.write("".join(json.dumps(e) + "\n" for e in entries))

    def made(self, *claim, chosen=()):
        """The generator due replies with its claim, by default each item it judges now passing,
        every item or on a remake each item sent back, naming the choices given; and what the
        script prints then."""
        run = self.state()
        claim = claim or tuple(
            dict(PASSED, checklist=i["checklist"], item=i["item"])
            for i in run["back"] or run["items"]
        )
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
        with mock.patch.object(flow, "SENDS", 0):
            return self.replied({"items": self.reading(*found)})

    def returned(self, out):
        """The return of the result as the script printed it, once every item has its Good, told
        where the result is; and what came with the line."""
        self.assertIn(f"The result is at {self.result}.", out["line"])
        return self.heard(out)


class ReadTest(RepoTest):
    """A run started, its generator due."""

    def setUp(self):
        super().setUp()
        self.started()
