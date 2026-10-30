"""What turn's tests share: a temporary folder standing for the user's repository, holding a task's
CCS, its checklist, its decisions and a work already written, turn run on it as the orchestrator
and each role run it, and the replies of a run, each written once here."""

import contextlib
import io
import json
import os
import sys
import time
from unittest import mock

TURN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "turn")
)
SCRIPTS = os.path.join(TURN, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(TURN, "..", "..", "dev", "lane"))

import call  # noqa: F401  (each of turn's modules, for its own tests)
import folder  # noqa: F401
import forms  # noqa: F401
import items as checklist_items  # noqa: F401
import parts as work_parts  # noqa: F401
import prompts  # noqa: F401
import testing
import turn
import wait  # noqa: F401

# The items of the run's checklist, by its path and ID.
ITEM_F1 = {"checklist": "checklists/readme.md", "item": "F-1"}
ITEM_B1 = {"checklist": "checklists/readme.md", "item": "B-1"}
ITEMS = [ITEM_F1, ITEM_B1]
CHECKLIST = """# README

A README is read by whoever meets the project first.

## Questions

### F-1: Shape

Does the README follow this template?

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
    "kind": {
        "work": "deliverable",
        "checklist": "checklist",
        "receiver": "audience",
        "use": "purpose",
        "has": "page",
        "each": "each",
    },
    "result": ".tasks/readme-result.json",
    "test": "sh tests/readme.sh",
}
RESULT = CALL["result"]
# The first user's Good for each item: the lines of the work that give it.
FOUND = {"checklist": "checklists/readme.md", "item": "F-1", "lines": ["README.md:1-3"]}
FOUND_B1 = dict(FOUND, item="B-1")
# An item the generator claims, at the lines of the work that give its Good.
MADE = dict(FOUND)
MADE_B1 = dict(FOUND_B1)
# A choice the work rests on that the CCS leaves open, as the generator names it.
CHOSEN = {"chosen": "the example tidies people.csv", "why": "no decision names a file"}
# The generator's claim of every item at its lines, naming the choice it made.
CLAIM = {"items": [MADE, MADE_B1], "chosen": [CHOSEN]}
# What the receiver would need to get an item's Good, as the first user gives it where it found
# none.
NEED = "Before trying it, the developer can tell whether it is for their own files."
NEEDED_F1 = dict(ITEM_F1, need=NEED)
NEEDED_B1 = dict(ITEM_B1, need=NEED)
# A first user's reading of every item: the Good it found for one, and what the receiver would need
# for the other; and one finding every Good.
FIRST_READ = {"items": [FOUND, NEEDED_B1]}
ALL_GOOD = {"items": [FOUND, FOUND_B1]}
# A checklist item, added to a run's checklist where a test needs one asked of each part of the
# work; the CCS asking it of each part, by the kind the call names; the work's parts, as the script
# splits a README of a title, an opening and one section; and its Good, at lines in each part.
EACH = """
### B-2: Each part used

Does the reader use each part toward their purpose?
"""
EACH_ITEM = {"checklist": "checklists/readme.md", "item": "B-2"}
EACH_CCS = dict(
    CCS, retrieved_artifacts=[*CCS["retrieved_artifacts"], {"each": "checklists/readme.md B-2"}]
)
SECTIONED = "# csvtidy\n\nTidies CSV files.\n\n## Use\n\nRun it.\n"
EACH_GOOD = {
    "checklist": "checklists/readme.md",
    "item": "B-2",
    "lines": ["README.md:3", "README.md:7"],
}
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

    def turn(self, *argv):
        """What turn.py gives back and prints, run with the arguments."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = turn.main(list(argv))
        return code, out.getvalue()

    def printed(self, *argv):
        """What turn.py prints as JSON, run with the arguments; fails the test where it stops."""
        code, out = self.turn(*argv)
        self.assertEqual(code, 0, out)
        return json.loads(out)

    def stopped(self, *argv):
        """What turn.py prints, run with the arguments, where it stops."""
        code, out = self.turn(*argv)
        self.assertEqual(code, 1, out)
        return out

    def started(self, asked=None):
        """The run started on a call, by default the run's; gives the result as the start printed
        it, a whole path."""
        return self.printed("start", json.dumps(asked or CALL))["result"]

    def here(self, path):
        """The path as a whole path in the folder the call was made from, as a role is given it."""
        return os.path.join(self.base, path)

    def kept(self, name):
        """The whole path of the file of the name in the folder the run of RESULT is kept in."""
        return self.here(f"{RUN}/{name}")

    def claimed(self, claim):
        """The generator writes its claim where it replies."""
        self.write(self.kept("generator.json"), json.dumps(claim))

    def read_as(self, reading):
        """The first user writes its reading where it replies."""
        self.write(self.kept("first-user.json"), json.dumps(reading))


class StartedTest(RepoTest):
    """A run started, `result` the whole path of its result."""

    def setUp(self):
        super().setUp()
        self.result = self.started()
