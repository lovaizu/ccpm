"""Tests for pith's PreToolUse hook, fed the JSON Claude Code sends, through the entry file."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "pith")
ENTRY = os.path.join(PLUGIN_ROOT, "hooks", "pretooluse.py")
HOOKS_JSON = os.path.join(PLUGIN_ROOT, "hooks", "hooks.json")
FIRST_USER = "pith:first-user"


def hook_input(tool_name, tool_input, agent_type=FIRST_USER):
    data = {
        "session_id": "abc123",
        "transcript_path": "/Users/someone/.claude/projects/repo/abc123.jsonl",
        "cwd": "/Users/someone/repo",
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": "toolu_01",
    }
    if agent_type is not None:
        data["agent_id"] = "agent-1"
        data["agent_type"] = agent_type
    return json.dumps(data)


def run_entry(stdin):
    return subprocess.run([sys.executable, ENTRY], input=stdin, capture_output=True, text=True)


class FirstUserHistoryTest(unittest.TestCase):

    def assertBlocked(self, result):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1)
        self.assertIn("first user does not read how the work was made", result.stderr)

    def assertPassed(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_first_user_reading_git_history_is_blocked(self):
        # Given
        commands = ("git log --oneline",
                    "git show HEAD~1:README.md",
                    "git blame README.md",
                    "git reflog",
                    "git stash list",
                    "git diff HEAD~1",
                    "git -C /Users/someone/repo log -3",
                    "git --no-pager -c core.pager=cat diff",
                    "cd repo && git log | head -5",
                    "ls; /usr/bin/git show HEAD",
                    'git log --format="%h;%s" -3')
        for command in commands:
            with self.subTest(command=command):
                # When
                result = run_entry(hook_input("Bash", {"command": command}))
                # Then
                self.assertBlocked(result)

    def test_first_user_running_other_commands_passes(self):
        # Given
        commands = ("git status", "git ls-files", "git -C repo rev-parse --show-toplevel",
                    "cat README.md | grep -n install", "python3 -m unittest")
        for command in commands:
            with self.subTest(command=command):
                # When
                result = run_entry(hook_input("Bash", {"command": command}))
                # Then
                self.assertPassed(result)

    def test_first_user_reaching_conversation_records_is_blocked(self):
        # Given
        cases = [
            ("Read", {"file_path": "/Users/someone/.claude/projects/repo/abc123.jsonl"}),
            ("Grep", {"pattern": "design", "path": "/Users/someone/.claude/projects/"}),
            ("Glob", {"pattern": "**/*.jsonl", "path": "/Users/someone/.claude/projects"}),
            ("Bash", {"command": "ls ~/.claude/projects/"}),
            ("Bash", {"command": "grep -r aim \"$HOME/.claude/projects\""}),
        ]
        for tool_name, tool_input in cases:
            with self.subTest(tool=tool_name, input=tool_input):
                # When
                result = run_entry(hook_input(tool_name, tool_input))
                # Then
                self.assertBlocked(result)

    def test_first_user_reading_the_work_passes(self):
        # Given
        cases = [
            ("Read", {"file_path": "/Users/someone/repo/README.md"}),
            ("Read", {"file_path": "/Users/someone/.claude/projects/repo/abc123/tool-results/b1.txt"}),
            ("Bash", {"command": "cat /Users/someone/.claude/projects/repo/abc/tool-results/b1.txt"}),
            ("Grep", {"pattern": "install", "path": "/Users/someone/repo"}),
            ("Glob", {"pattern": "**/*.md", "path": "/Users/someone/repo/.claude/rules"}),
        ]
        for tool_name, tool_input in cases:
            with self.subTest(tool=tool_name, input=tool_input):
                # When
                result = run_entry(hook_input(tool_name, tool_input))
                # Then
                self.assertPassed(result)

    def test_other_agents_reading_history_or_records_pass(self):
        # Given
        agent_types = ("pith:generator", "general-purpose", None)
        for agent_type in agent_types:
            with self.subTest(agent_type=agent_type):
                # When
                git_log = run_entry(hook_input("Bash", {"command": "git log -3"}, agent_type))
                records = run_entry(hook_input(
                    "Read", {"file_path": "/Users/someone/.claude/projects/repo/a.jsonl"}, agent_type))
                # Then
                self.assertPassed(git_log)
                self.assertPassed(records)


class HooksJsonWithoutPythonTest(unittest.TestCase):
    """The command in hooks.json, run by sh with no python3 on PATH."""

    def setUp(self):
        with open(HOOKS_JSON, encoding="utf-8") as handle:
            hook = json.load(handle)["hooks"]["PreToolUse"][0]["hooks"][0]
        self.command = hook["command"]
        self.bin = tempfile.mkdtemp()
        os.symlink(shutil.which("cat"), os.path.join(self.bin, "cat"))

    def tearDown(self):
        shutil.rmtree(self.bin)

    def run_without_python(self, stdin):
        env = {"PATH": self.bin, "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT}
        return subprocess.run(["/bin/sh", "-c", self.command], input=stdin, env=env,
                              capture_output=True, text=True)

    def test_without_python_first_user_is_blocked_and_told_to_install(self):
        # Given
        stdins = (hook_input("Read", {"file_path": "/Users/someone/repo/README.md"}),
                  hook_input("Bash", {"command": "ls"}).replace('": "', '":"'))
        for stdin in stdins:
            with self.subTest(stdin=stdin[:40]):
                # When
                result = self.run_without_python(stdin)
                # Then
                self.assertEqual(result.returncode, 2)
                self.assertIn("install Python 3.9 or later", result.stderr)

    def test_without_python_other_agents_pass(self):
        # Given
        stdin = hook_input("Bash", {"command": "echo agent_type pith:first-user"}, "general-purpose")
        # When
        result = self.run_without_python(stdin)
        # Then
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_with_python_the_entry_file_blocks_git_log(self):
        # Given
        env = {"PATH": os.path.dirname(sys.executable) + os.pathsep + self.bin,
               "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT}
        # When
        result = subprocess.run(["/bin/sh", "-c", self.command],
                                input=hook_input("Bash", {"command": "git log"}),
                                env=env, capture_output=True, text=True)
        # Then
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("first user does not read how the work was made", result.stderr)


if __name__ == "__main__":
    unittest.main()
