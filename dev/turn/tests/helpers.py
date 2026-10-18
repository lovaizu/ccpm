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

import pretooluse  # noqa: F401  (the hooks' entry, for the hooks' tests)
import subagentstop

import turn

CHECKLIST = """# README

A README is read by whoever meets the project first.

## Format

### F-1: Shape

Does the README follow this template?

## Benefit

### B-1: Who it is for

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
LEARNT = [
    {
        "checklist": "checklists/readme.md",
        "item": "F-1",
        "learnt": "the name and the opening first",
    },
    {"checklist": "checklists/readme.md", "item": "B-1", "learnt": "say whom it is for in line 3"},
]
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
SENT_BACK = {
    "checklist": "checklists/readme.md",
    "item": "B-1",
    "gets": "the reader sees at once that it is for CSV files",
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
            code = turn.main(list(argv), io.StringIO(stdin))
        return code, out.getvalue()

    def started(self, call=None):
        """The run started on a call, and the prompt the generator is to be started with."""
        code, out = self.turn("start", json.dumps(call or CALL))
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
        """The run taken through the orchestrator's findings, the first user's reply and the
        evaluator's, and what the script prints then."""
        out = self.next({"items": list(findings), "questions": [QUESTION]})
        reply = {"items": list(found)}
        self.assertEqual(self.replied("turn:first-user", out["prompt"], reply, *opened), (0, ""))
        out = self.next()
        self.assertEqual(out["agent"], "turn:evaluator")
        reply = {"items": list(evaluated)}
        self.assertEqual(self.replied("turn:evaluator", out["prompt"], reply), (0, ""))
        return self.next()

    def given_record(self, agent_id, prompt, *tool_uses):
        """Writes what Claude Code keeps of an agent's conversation: its prompt as the first record,
        then each tool it used, kept twice under one ID as Claude Code keeps it."""
        path = os.path.join(self.repo, "session", "subagents", f"agent-{agent_id}.jsonl")
        records = [{"type": "user", "message": {"role": "user", "content": prompt}}]
        records += [
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "I open it."},
                        {"type": "tool_use", "id": f"toolu_{n}", "name": name, "input": tool_input},
                    ],
                },
            }
            for n, (name, tool_input) in enumerate(tool_uses)
            for _ in range(2)
        ]
        self.write(path, "".join(json.dumps(r) + "\n" for r in records))
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

    def hook(self, entry, event):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = entry.main(io.StringIO(json.dumps(event)))
        return code, err.getvalue()

    def replied(self, agent_type, prompt, reply, *tool_uses):
        """A role started with the prompt ends with the reply, after using the tools, as turn's
        SubagentStop hook sees it; given no tools, a reader has read the work and the checklist
        whole."""
        if not tool_uses and agent_type != "turn:learner":
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
