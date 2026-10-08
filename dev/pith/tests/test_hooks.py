"""Tests for pith's hooks, fed the input Claude Code hands them: the CCS check before the first user
starts, and the facts written from the first user's JSONL when it stops."""

import io
import json
import os
import runpy
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest import mock

SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "pith", "scripts")
sys.path.insert(0, SCRIPTS)

import ccs  # noqa: E402
import check_in  # noqa: E402
import facts  # noqa: E402

READY = """semantic_gist:
  - investigate: "use the work as its receiver would"
focal_entities:
  - work: ".github/prompts/pr-review.md"
  - receiver: "Claude in CI"
goal_orientation:
  - use: "write a comment on each pull request"
constraints:
  - language: "Japanese"
retrieved_artifacts:
  - essentials: "/plugin/references/essentials/prompt.md"
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
        os.makedirs(os.path.join(self.root, ".pith"))
        self.ccs = os.path.join(self.root, ".pith", "pr-review.yaml")

    def tearDown(self):
        self.dir.cleanup()

    def write_ccs(self, text):
        with open(self.ccs, "w") as f:
            f.write(text)

    def check(self, args, skill="pith:use"):
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

    def test_a_missing_receiver_stops_the_call_and_says_where_it_comes_from(self):
        # Given
        self.write_ccs(READY.replace('  - receiver: "Claude in CI"\n', ""))
        # When
        code, said = self.check(self.ccs)
        # Then
        self.assertEqual(code, 2)
        self.assertIn("focal_entities: receiver (from the caller: who uses the work)", said)

    def test_an_open_gap_stops_the_call(self):
        # Given
        self.write_ccs(READY + 'uncertainty_signal:\n  - gap: "which prompt runs in CI"\n')
        # When
        code, said = self.check(self.ccs)
        # Then
        self.assertEqual(code, 2)
        self.assertIn("Open gaps: which prompt runs in CI", said)

    def test_a_call_without_a_ccs_path_is_stopped(self):
        # Given
        self.write_ccs(READY)
        # When
        code, said = self.check("check the prompt in .github/prompts/pr-review.md")
        # Then
        self.assertEqual(code, 2)
        self.assertIn("Hand the first user the path of its CCS", said)

    def test_a_ccs_the_caller_keeps_in_the_repository_is_found_from_its_relative_path(self):
        # Given
        os.makedirs(os.path.join(self.root, ".rn"))
        with open(os.path.join(self.root, ".rn", "use.yaml"), "w") as f:
            f.write(READY)
        # When
        code, said = self.check(".rn/use.yaml")
        # Then
        self.assertEqual((code, said), (0, ""))

    def test_another_skill_is_never_stopped(self):
        # Given no CCS at all
        # When
        code, said = self.check("anything", skill="writ:up")
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
            self.use("a", "Read", {"file_path": os.path.join(self.root, ".github/prompts/pr-review.md")}),
            self.result("a", "the prompt"),
            self.use("a2", "Read", {"file_path": os.path.join(self.root, ".github/prompts/pr-review.md")}),
            self.result("a2", "the prompt"),
            self.use("b", "Bash", {"command": "claude -p " + "x" * 200}),
            self.result("b", "NO_COMMENT"),
            self.use("b2", "Bash", {"command": "cat .github/prompts/pr-review.good.md"}),
            self.result("b2", "the old prompt"),
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

    def test_what_the_first_user_did_is_written_from_its_jsonl(self):
        # Given
        self.write_ccs(READY)
        transcript = self.first_user_run()
        # When
        run(facts, {"agent_type": "pith:first-user", "agent_transcript_path": transcript, "cwd": self.root})
        # Then
        state = ccs.load(self.ccs)
        self.assertEqual(state["episodic_trace"], [
            ("executed", "claude -p " + "x" * 150 + "… → exit 0"),
            ("executed", "cat .github/prompts/pr-review.good.md → exit 0"),
            ("failed", "ls /nonexistent → exit 1"),
            ("failed", "false → exit 1"),
            ("failed", "sleep 999 → exit None"),
            ("wrote", os.path.join(self.root, "notes.md")),
            ("wrote_outside", "/tmp/elsewhere.md"),
        ])
        self.assertEqual(state["retrieved_artifacts"], [
            ("essentials", "/plugin/references/essentials/prompt.md"),
            ("read", ".github/prompts/pr-review.md"),
            ("transcript", transcript),
        ])
        self.assertEqual(state["focal_entities"][0], ("work", ".github/prompts/pr-review.md"))
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

    def test_a_first_user_handed_no_ccs_writes_nothing(self):
        # Given
        transcript = self.transcript([{"type": "user", "message": {"content": [{"type": "text", "text": "no path"}]}}])
        # When
        run(facts, {"agent_type": "pith:first-user", "agent_transcript_path": transcript, "cwd": self.root})
        # Then
        self.assertFalse(os.path.exists(self.ccs))


if __name__ == "__main__":
    unittest.main()
