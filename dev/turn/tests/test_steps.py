"""Tests for turning an agent's conversation record into its numbered steps."""

import json
import os
import shutil
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "scripts"))

import steps  # noqa: E402


def use(n, name, given):
    return {"type": "assistant", "message": {"content": [
        {"type": "text", "text": "thinking"}, {"type": "tool_use", "id": f"t{n}", "name": name, "input": given}]}}


def result(n, content, error=False):
    return {"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": f"t{n}", "content": content, "is_error": error}]}}


class StepsTest(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.record = os.path.join(self.root, "agent-x.jsonl")

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, entries):
        with open(self.record, "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(e) + "\n" for e in entries))

    def test_each_tool_call_is_a_numbered_step_with_what_it_did_and_what_came_out(self):
        # Given
        self.write([{"type": "user", "message": {"content": "use the guide"}},
                    use(1, "Read", {"file_path": "/c/SETUP.md"}),
                    result(1, [{"type": "text", "text": "     1\t# Setup"}]),
                    use(2, "Bash", {"command": "npm start\necho done"}),
                    result(2, "Exit code 1\nmissing var/", error=True)])

        # When
        found = steps.steps(self.record, "first-user-1")

        # Then
        self.assertEqual(found, [
            {"step": "first-user-1#1", "did": "Read /c/SETUP.md", "came_out": "     1\t# Setup",
             "error": False},
            {"step": "first-user-1#2", "did": "Bash npm start\necho done",
             "came_out": "Exit code 1\nmissing var/", "error": True}])

    def test_a_call_with_no_result_yet_is_a_step_that_shows_nothing_came_out(self):
        # Given
        self.write([use(1, "Write", {"file_path": "/r/NOTE.md", "content": "x"})])

        # When
        found = steps.steps(self.record, "generator-2")

        # Then
        self.assertEqual(found, [{"step": "generator-2#1", "did": "Write /r/NOTE.md", "came_out": "",
                                  "error": False}])

    def test_a_tool_without_a_place_or_command_shows_its_input(self):
        # Given
        self.write([use(1, "Grep", {"pattern": "token", "path": "src"}), result(1, "src/a.py")])

        # When
        found = steps.steps(self.record, "learner-1")

        # Then
        self.assertEqual(found[0]["did"], 'Grep {"pattern": "token", "path": "src"}')

    def test_a_long_output_keeps_its_head_and_tail_and_says_how_much_is_left_out(self):
        # Given
        lines = [f"line {i}" for i in range(1, 101)]
        self.write([use(1, "Bash", {"command": "seq"}), result(1, "\n".join(lines))])

        # When
        out = steps.steps(self.record, "first-user-1")[0]["came_out"].splitlines()

        # Then
        self.assertEqual(out[:30], lines[:30])
        self.assertEqual(out[30], "(60 lines left out)")
        self.assertEqual(out[31:], lines[-10:])

    def test_the_steps_are_written_for_reading_and_for_scripts(self):
        # Given
        self.write([use(1, "Bash", {"command": "ls"}), result(1, "a\nb", error=True)])
        found = steps.steps(self.record, "first-user-1")

        # When
        steps.write(self.root, "first-user-1", found)

        # Then
        with open(os.path.join(self.root, "steps-first-user-1.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f), found)
        with open(os.path.join(self.root, "steps-first-user-1.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# Steps of first-user-1\n\n## first-user-1#1 (error)\n\nDid: Bash ls\n\n"
                                       "Came out:\n\n```\na\nb\n```\n")


if __name__ == "__main__":
    unittest.main()
