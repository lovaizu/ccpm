"""Tests for writ's hooks, fed the input Claude Code hands them: the CCS check before the generator
starts, and the facts written from the generator's JSONL when it stops."""

import io
import json
import os
import runpy
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest import mock

SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "writ", "scripts")
sys.path.insert(0, SCRIPTS)

import ccs  # noqa: E402
import check_in  # noqa: E402
import facts  # noqa: E402

READY = """focal_entities:
  - work: "docs/migration-plan.md"
constraints:
  - language: "English"
retrieved_artifacts:
  - plan: ".writ/open/01-notes-migration-plan.md"
  - essentials: "/pith/references/essentials/doc.md"
  - style: "/pith/references/style.md"
  - read: "old.md"
"""


def run(module, hook):
    """Run the hook's script as Claude Code runs it, with the hook input on stdin."""
    with mock.patch("sys.stdin", io.StringIO(json.dumps(hook))):
        runpy.run_path(module.__file__, run_name="__main__")


class Repo(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.dir.name)
        os.makedirs(os.path.join(self.root, ".writ"))
        self.ccs = os.path.join(self.root, ".writ", "migration-plan-make.yaml")

    def tearDown(self):
        self.dir.cleanup()

    def write_ccs(self, text):
        with open(self.ccs, "w") as f:
            f.write(text)

    def check(self, args, skill="writ:make"):
        """The check's exit status and what it said."""
        err = io.StringIO()
        with redirect_stderr(err):
            try:
                run(check_in, {"cwd": self.root, "tool_input": {"skill": skill, "args": args}})
            except SystemExit as stop:
                return stop.code, err.getvalue()
        return 0, err.getvalue()


class CheckIn(Repo):
    def test_a_ready_ccs_lets_the_first_user_start(self):
        # Given
        self.write_ccs(READY)
        # When
        code, said = self.check(self.ccs)
        # Then
        self.assertEqual((code, said), (0, ""))

    def test_a_missing_plan_stops_the_call_and_says_where_it_comes_from(self):
        # Given
        self.write_ccs(READY.replace('  - plan: ".writ/open/01-notes-migration-plan.md"\n', ""))
        # When
        code, said = self.check(self.ccs)
        # Then
        self.assertEqual(code, 2)
        self.assertIn("retrieved_artifacts: plan (from the plan the user agreed, with its pass condition)", said)

    def test_an_open_gap_stops_the_call(self):
        # Given
        self.write_ccs(READY + 'uncertainty_signal:\n  - gap: "whether cli/ is included"\n')
        # When
        code, said = self.check(self.ccs)
        # Then
        self.assertEqual(code, 2)
        self.assertIn("Open gaps: whether cli/ is included", said)

    def test_a_call_without_a_ccs_path_is_stopped(self):
        # Given
        self.write_ccs(READY)
        # When
        code, said = self.check("write docs/migration-plan.md")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("Hand the path of its CCS", said)

    def test_a_ccs_is_found_from_its_path_relative_to_the_repository(self):
        # Given
        self.write_ccs(READY)
        # When
        code, said = self.check(".writ/migration-plan-make.yaml")
        # Then
        self.assertEqual((code, said), (0, ""))

    def test_another_skill_is_never_stopped(self):
        # Given no CCS at all
        # When
        code, said = self.check("anything", skill="pith:use")
        # Then
        self.assertEqual((code, said), (0, ""))


class Facts(Repo):
    def transcript(self, entries):
        path = os.path.join(self.root, "agent.jsonl")
        with open(path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        return path

    def use(self, uid, name, args):
        return {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": uid, "name": name, "input": args}]}}

    def result(self, uid, content, error=False):
        return {"type": "user", "message": {"content": [
            {"type": "tool_result", "tool_use_id": uid, "content": content, "is_error": error}]}}

    def first_user_run(self):
        return self.transcript([
            {"type": "user", "message": {"content": self.ccs}},
            self.use("a", "Read", {"file_path": os.path.join(self.root, "docs/architecture.md")}),
            self.result("a", "the architecture"),
            self.use("a2", "Read", {"file_path": os.path.join(self.root, "docs/architecture.md")}),
            self.result("a2", "the architecture"),
            self.use("b", "Bash", {"command": "claude -p " + "x" * 200}),
            self.result("b", "NO_COMMENT"),
            self.use("b2", "Bash", {"command": "cat docs/typing-guide.md"}),
            self.result("b2", "the guide"),
            self.use("c", "Bash", {"command": "ls /nonexistent"}),
            self.result("c", "Exit code 1\nls: /nonexistent: No such file", error=True),
            self.use("d", "Bash", {"command": "false"}),
            self.result("d", [{"type": "text", "text": "failed"}], error=True),
            self.use("e", "Bash", {"command": "sleep 999"}),
            self.use("f", "Write", {"file_path": os.path.join(self.root, "notes.md")}),
            self.result("f", "ok"),
            self.use("g", "Edit", {"file_path": "/tmp/elsewhere.md"}),
            self.result("g", "ok"),
            {"type": "attachment"},
        ])

    def test_what_the_generator_did_is_written_from_its_jsonl(self):
        # Given
        self.write_ccs(READY)
        transcript = self.first_user_run()
        # When
        run(facts, {"agent_type": "writ:generator", "agent_transcript_path": transcript, "cwd": self.root})
        # Then
        state = ccs.load(self.ccs)
        self.assertEqual(state["episodic_trace"], [
            ("executed", "claude -p " + "x" * 150 + "… → exit 0"),
            ("executed", "cat docs/typing-guide.md → exit 0"),
            ("failed", "ls /nonexistent → exit 1"),
            ("failed", "false → exit 1"),
            ("failed", "sleep 999 → exit None"),
            ("wrote", os.path.join(self.root, "notes.md")),
            ("wrote_outside", "/tmp/elsewhere.md"),
        ])
        self.assertEqual(state["retrieved_artifacts"], [
            ("plan", ".writ/open/01-notes-migration-plan.md"),
            ("essentials", "/pith/references/essentials/doc.md"),
            ("style", "/pith/references/style.md"),
            ("read", "docs/architecture.md"),
            ("transcript", transcript),
        ])
        self.assertEqual(state["focal_entities"][0], ("work", "docs/migration-plan.md"))
        self.assertEqual(state["relational_map"], [])

    def test_another_agent_leaves_the_ccs_untouched(self):
        # Given
        self.write_ccs(READY)
        transcript = self.first_user_run()
        # When
        run(facts, {"agent_type": "", "agent_transcript_path": transcript, "cwd": self.root})
        # Then
        with open(self.ccs) as f:
            self.assertEqual(f.read(), READY)

    def test_a_generator_handed_no_ccs_writes_nothing(self):
        # Given
        transcript = self.transcript([{"type": "user", "message": {"content": [{"type": "text", "text": "no path"}]}}])
        # When
        run(facts, {"agent_type": "writ:generator", "agent_transcript_path": transcript, "cwd": self.root})
        # Then
        self.assertFalse(os.path.exists(self.ccs))


if __name__ == "__main__":
    unittest.main()
