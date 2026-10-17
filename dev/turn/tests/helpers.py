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
HOOKS = os.path.join(TURN, "hooks")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, HOOKS)

import pretooluse  # noqa: F401  (the hooks' entries, for the hooks' tests)
import subagentstop  # noqa: F401

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
SENT_BACK = {
    "checklist": "checklists/readme.md",
    "item": "B-1",
    "gets": "the reader sees at once that it is for CSV files",
}


class RepoTest(unittest.TestCase):
    """Each test runs turn from a temporary folder standing for the user's repository, holding a
    task's CCS, its checklist, its decisions and a work already written."""

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.repo)
        self.write_json(CALL["ccs"], CCS)
        self.write("checklists/readme.md", CHECKLIST)
        self.write("notes/readme.decisions.md", "# Decisions\n")
        self.write("docs/start.md", "# Start\n")
        self.write("README.md", "# csvtidy\n\nTidies CSV files.\n")

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
