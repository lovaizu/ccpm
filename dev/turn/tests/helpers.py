import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

TURN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
)
SCRIPTS = os.path.join(TURN, "scripts")
# How the orchestrator runs turn's script, as its prompt gives it.
SCRIPT = f'python3 "{os.path.join(TURN, "scripts", "turn.py")}"'
HOOKS = os.path.join(TURN, "hooks")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, HOOKS)

import agents  # noqa: F401  (the hooks' reading of an event, for its own tests)
import events
import forms  # noqa: F401  (the forms, for their own tests)
import records
import run
from checks import (  # noqa: F401  (each check, for its own tests)
    call_given,
    no_commit,
    read_in_given,
    read_whole,
    role_given,
    start_as_called,
)

# The checks each entry of the hooks runs, which a test hands an event as that entry would.
pretooluse = events.PRETOOLUSE
subagentstop = events.SUBAGENTSTOP

CHECKLIST = """---
name: readme
check: usability
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
# A checklist answered against the sources, which the first user and the evaluator are not given;
# a CCS naming it beside the README's; and its item's Good, as the orchestrator finds it.
ACCURACY = """---
name: accuracy
check: accuracy
version: 0.1.0
---

# Accuracy

## Benefit

### B-1: As decided

Scope: whole

Does the work carry out what its sources decided?
"""
ACCURATE = {
    "checklist": "checklists/accuracy.md",
    "item": "B-1",
    "good": "it tidies CSV files, as the decisions say",
    "lines": ["README.md:3-3"],
}
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
    "kind": {"work": "deliverable", "checklist": "checklist", "receiver": "audience"},
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
ID = "a1b2c3"
# What a first user and an evaluator read whole before they reply: the work and the checklist.
READ_SHOWN = (
    ("Read", {"file_path": "README.md"}),
    ("Read", {"file_path": "checklists/readme.md"}),
)
# What a generator and an orchestrator read whole: the CCS and every file it names.
READ_GIVEN = READ_SHOWN + (
    ("Read", {"file_path": ".tasks/readme.json"}),
    ("Read", {"file_path": "notes/readme.decisions.md"}),
    ("Read", {"file_path": "docs/start.md"}),
)
# The orchestrator's check before the work is made: what in the CCS and its files gives each item's
# Good.
CAN = [
    {"checklist": "checklists/readme.md", "item": "F-1", "can": "the template the checklist gives"},
    {"checklist": "checklists/readme.md", "item": "B-1", "can": "the receiver the CCS names"},
]
# A statement of the work with the words of the CCS's files it rests on, as the generator quotes
# them; the orchestrator's own mark of it; and one the orchestrator sends back, its source not
# found.
STATEMENT = {
    "lines": ["README.md:3-3"],
    "kind": "decision",
    "quotes": [{"path": "notes/readme.decisions.md", "quote": "# Decisions"}],
}
MARKED = {"lines": ["README.md:3-3"], "kind": "decision"}
UNSOURCED = {"lines": ["README.md:3-3"], "gets": "no file the CCS names says it tidies CSV files"}
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
# An item the first user finds no Good for, with the places of the work where it looked for it.
STOPPED = {"checklist": "checklists/readme.md", "item": "B-1", "places": ["README.md:3-3"]}
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


class RepoTest(unittest.TestCase):
    """Each test runs turn from a temporary folder standing for the user's repository, holding a
    task's CCS, its checklist, its decisions and a work already written."""

    def setUp(self):
        self.repo = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.repo)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.repo)
        self.write_json(CALL["ccs"], CCS)
        self.write("checklists/readme.md", CHECKLIST)
        self.write("notes/readme.decisions.md", "# Decisions\n")
        self.write("docs/start.md", "# Start\n")
        self.write("README.md", "# csvtidy\n\nTidies CSV files.\n")

        self.transcript = os.path.join(self.repo, "session.jsonl")

    def turn(self, *argv, stdin=""):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run.main(list(argv), io.StringIO(stdin))
        return code, out.getvalue()

    def started(self, call=None):
        """The run started on a call and checked to give every item its Good, and the prompt the
        generator is to be started with."""
        call = call or CALL
        code, out = self.turn("start", json.dumps(call))
        self.assertEqual(code, 0, out)
        check = json.dumps({"items": CAN, "questions": []})
        code, out = self.turn("next", call["result"], stdin=check)
        self.assertEqual(code, 0, out)
        return json.loads(out)["prompt"]

    def given(self):
        """What the role to start next is given, as the script prints it to the role."""
        code, out = self.turn("given", CALL["result"])
        self.assertEqual(code, 0, out)
        return json.loads(out)

    def next(self, given=None):
        """What the script prints next for the run, handed the orchestrator's reading or decision."""
        code, out = self.turn("next", CALL["result"], stdin=json.dumps(given) if given else "")
        self.assertEqual(code, 0, out)
        return json.loads(out)

    def refused(self, given=None):
        """What the script prints when it refuses to go on with the run."""
        code, out = self.turn("next", CALL["result"], stdin=json.dumps(given) if given else "")
        self.assertEqual(code, 1, out)
        return out

    def through(self, *evaluated, findings=(GOOD, WAITS), found=(FOUND,), opened=()):
        """The run taken through the orchestrator's findings, the first user's reading, after the
        round has sent it back as often as it may, and the evaluator's Goods; and what the script
        prints then."""
        out = self.next({"items": list(findings), "questions": [QUESTION], "statements": [MARKED]})
        kept = self.read_json(CALL["result"])
        kept["running"]["sent"] = {run.FIRST_USER: run.SENDS}
        self.write_json(CALL["result"], kept)
        reply = {"items": self.reading(*found)}
        self.assertEqual(self.replied("turn:first-user", out["prompt"], reply, *opened), (0, ""))
        out = self.next()
        self.assertEqual(out["agent"], "turn:evaluator")
        reply = {"items": list(evaluated)}
        self.assertEqual(self.replied("turn:evaluator", out["prompt"], reply), (0, ""))
        return self.next()

    def reading(self, *found):
        """A first user's reading giving the Goods found, and every other item it is given the
        places it looked for its Good."""
        kept = self.read_json(CALL["result"])["running"]
        given = {(i["checklist"], i["item"]) for i in found}
        return list(found) + [
            dict(i, places=["README.md:1-1"])
            for i in kept["usable"]
            if (i["checklist"], i["item"]) not in given
        ]

    def given_record(self, agent_id, prompt, *tool_uses):
        """Writes what Claude Code keeps of an agent's conversation: its prompt as the first record,
        then each tool it used, kept twice under one ID as Claude Code keeps it, with what the tool
        gave back where the use names it third."""
        path = os.path.join(self.repo, "session", "subagents", f"agent-{agent_id}.jsonl")
        entries = [{"type": "user", "message": {"role": "user", "content": prompt}}]
        for n, (name, tool_input, *back) in enumerate(tool_uses):
            used = {"type": "tool_use", "id": f"toolu_{n}", "name": name, "input": tool_input}
            content = [{"type": "text", "text": "I open it."}, used]
            entry = {"type": "assistant", "message": {"role": "assistant", "content": content}}
            entries += [entry, entry]
            if back:
                result = {"type": "tool_result", "tool_use_id": f"toolu_{n}", "content": back[0]}
                entries.append({"type": "user", "message": {"role": "user", "content": [result]}})
        self.write(path, "".join(json.dumps(r) + "\n" for r in entries))
        return path

    def event(self, name, agent_type=None, **fields):
        event = {
            "session_id": "s",
            "transcript_path": self.transcript,
            "cwd": self.repo,
            "hook_event_name": name,
            **fields,
        }
        if agent_type:
            event.update(agent_id=ID, agent_type=agent_type)
        return event

    def hook(self, checks, event):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = events.main(checks, io.StringIO(json.dumps(event)))
        return code, err.getvalue()

    def replied(self, agent_type, prompt, reply, *tool_uses):
        """A role started with the prompt ends with the reply, after using the tools, as turn's
        SubagentStop hook sees it; given no tools, a reader has read the work and the checklist
        whole."""
        if not tool_uses and agent_type == "turn:learner":
            tool_uses = self.pages_shown(prompt)
        elif not tool_uses:
            tool_uses = READ_SHOWN
        path = self.given_record(agent_type.partition(":")[2], prompt, *tool_uses)
        event = self.event(
            "SubagentStop",
            agent_type,
            agent_transcript_path=path,
            last_assistant_message=reply if isinstance(reply, str) else json.dumps(reply),
            stop_hook_active=False,
        )
        return self.hook(subagentstop, event)

    def learnt(self, out, reply=None, taken=None):
        """The learner started as the script printed, replying with what it found, by default no
        lesson on the run; then what the orchestrator takes, by default every lesson offered; and
        what the script prints after."""
        self.assertEqual(out["agent"], "turn:learner")
        reply = reply or {"process": [], "checked": CHECKED}
        self.assertEqual(self.replied("turn:learner", out["prompt"], reply), (0, ""))
        out = self.next()
        if "take" in out:
            every = list(range(1, len(out["take"]["process"]) + 1))
            out = self.next(taken or {"process": every})
        return out

    def pages_shown(self, prompt):
        """A learner's commands showing every page of every record of its run."""
        kept = run.running(json.loads(prompt)["run"])
        paths = run.learnt_from(kept) if kept else []
        return tuple(
            ("Bash", {"command": f"{SCRIPT} record {json.loads(prompt)['run']} {n} {p}"})
            for n, path in enumerate(paths, 1)
            for p in range(1, len(records.pages(path)) + 1)
        )

    def with_accuracy(self):
        """The task's CCS names the accuracy checklist too, after the README's."""
        self.write("checklists/accuracy.md", ACCURACY)
        artifacts = CCS["retrieved_artifacts"]
        ccs = dict(
            CCS,
            retrieved_artifacts=artifacts[:1]
            + [{"checklist": "checklists/accuracy.md"}]
            + artifacts[1:],
        )
        self.write_json(CALL["ccs"], ccs)

    def write(self, path, text):
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def write_json(self, path, data):
        self.write(path, json.dumps(data))

    def read_json(self, path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
