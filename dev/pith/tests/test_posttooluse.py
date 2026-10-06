"""Tests for pith's PostToolUse hook: a result file written is checked against its form."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "pith")
ENTRY = os.path.join(PLUGIN_ROOT, "hooks", "posttooluse.py")
HOOKS_JSON = os.path.join(PLUGIN_ROOT, "hooks", "hooks.json")

RESULT = textwrap.dedent("""\
    # Check: docs/guide.md

    Target: docs/guide.md
    Receiver and purpose: a new engineer setting up
    Essentials: essentials/doc.md
    Aim: they set up alone.

    ## doc.md: What did you do?

    Report: I ran make setup and it worked.

    - Good: `docs/guide.md:1` the reader sets up alone
      - Evidence (work): "Run make setup"
    """)


class ResultFormHookTest(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.write("docs/guide.md", "Run make setup.\n")
        self.write("essentials/doc.md", "# Doc\n\n- What did you do?\n")

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, path, text):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)
        return full

    def run_hook(self, path, tool_name="Write"):
        data = {"session_id": "s1", "cwd": self.root, "hook_event_name": "PostToolUse",
                "tool_name": tool_name, "tool_input": {"file_path": path}}
        return subprocess.run([sys.executable, ENTRY], input=json.dumps(data),
                              capture_output=True, text=True)

    def test_a_result_file_in_form_passes(self):
        # Given
        path = self.write(".pith/open/01-report-guide.md", RESULT)
        # When
        result = self.run_hook(path)
        # Then
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_a_result_file_out_of_form_is_sent_back_with_its_problems(self):
        # Given
        path = self.write(".rn/20261007-x/open/03-report-task-3.md",
                          RESULT.replace('"Run make setup"', '"Run make install"'))
        # When
        result = self.run_hook(path, "Edit")
        # Then
        self.assertEqual(result.returncode, 2)
        self.assertIn("out of its form", result.stderr)
        self.assertIn("evidence (work) not found in docs/guide.md", result.stderr)

    def test_files_that_are_not_result_files_pass(self):
        # Given
        paths = (self.write("docs/open/notes.md", "# Notes\n"),
                 self.write("docs/guide-copy.md", RESULT),
                 self.write(".pith/open/02-report-x.txt", RESULT),
                 os.path.join(self.root, ".pith/open/03-report-gone.md"))
        for path in paths:
            with self.subTest(path=path):
                # When
                result = self.run_hook(path)
                # Then
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")


class PostToolUseWithoutPythonTest(unittest.TestCase):
    """The command in hooks.json, run by sh with no python3 on PATH."""

    def setUp(self):
        with open(HOOKS_JSON, encoding="utf-8") as handle:
            self.command = json.load(handle)["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
        self.bin = tempfile.mkdtemp()
        os.symlink(shutil.which("cat"), os.path.join(self.bin, "cat"))

    def tearDown(self):
        shutil.rmtree(self.bin)

    def run_without_python(self, path):
        stdin = json.dumps({"tool_name": "Write", "tool_input": {"file_path": path}})
        return subprocess.run(["/bin/sh", "-c", self.command], input=stdin,
                              env={"PATH": self.bin, "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT},
                              capture_output=True, text=True)

    def test_without_python_a_result_file_written_is_stopped_and_told_to_install(self):
        # When
        result = self.run_without_python("/repo/.pith/open/01-report-guide.md")
        # Then
        self.assertEqual(result.returncode, 2)
        self.assertIn("install Python 3.9 or later", result.stderr)

    def test_without_python_other_files_pass(self):
        # When
        result = self.run_without_python("/repo/docs/guide.md")
        # Then
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
