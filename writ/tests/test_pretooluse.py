"""Tests for writ's PreToolUse hook, fed the JSON Claude Code sends, through the entry file."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY = os.path.join(PLUGIN_ROOT, "hooks", "pretooluse.py")
HOOKS_JSON = os.path.join(PLUGIN_ROOT, "hooks", "hooks.json")
FIRST_USER = "writ:first-user"


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

    def test_given_first_user_when_bash_runs_git_history_then_blocked(self):
        for command in ("git log --oneline",
                        "git show HEAD~1:README.md",
                        "git blame README.md",
                        "git reflog",
                        "git stash list",
                        "git diff HEAD~1",
                        "git -C /Users/someone/repo log -3",
                        "git --no-pager -c core.pager=cat diff",
                        "cd repo && git log | head -5",
                        "ls; /usr/bin/git show HEAD"):
            with self.subTest(command=command):
                self.assertBlocked(run_entry(hook_input("Bash", {"command": command})))

    def test_given_first_user_when_bash_runs_other_git_or_commands_then_passes(self):
        for command in ("git status", "git ls-files", "git -C repo rev-parse --show-toplevel",
                        "cat README.md | grep -n install", "python3 -m unittest"):
            with self.subTest(command=command):
                self.assertPassed(run_entry(hook_input("Bash", {"command": command})))

    def test_given_first_user_when_tool_reaches_conversation_records_then_blocked(self):
        cases = [
            ("Read", {"file_path": "/Users/someone/.claude/projects/repo/abc123.jsonl"}),
            ("Grep", {"pattern": "design", "path": "/Users/someone/.claude/projects/"}),
            ("Glob", {"pattern": "**/*.jsonl", "path": "/Users/someone/.claude/projects"}),
            ("Bash", {"command": "ls ~/.claude/projects/"}),
            ("Bash", {"command": "grep -r aim \"$HOME/.claude/projects\""}),
        ]
        for tool_name, tool_input in cases:
            with self.subTest(tool=tool_name, input=tool_input):
                self.assertBlocked(run_entry(hook_input(tool_name, tool_input)))

    def test_given_first_user_when_tool_reads_the_work_then_passes(self):
        cases = [
            ("Read", {"file_path": "/Users/someone/repo/README.md"}),
            ("Grep", {"pattern": "install", "path": "/Users/someone/repo"}),
            ("Glob", {"pattern": "**/*.md", "path": "/Users/someone/repo/.claude/rules"}),
        ]
        for tool_name, tool_input in cases:
            with self.subTest(tool=tool_name, input=tool_input):
                self.assertPassed(run_entry(hook_input(tool_name, tool_input)))

    def test_given_other_agent_or_main_conversation_when_git_log_or_records_then_passes(self):
        for agent_type in ("writ:generator", "general-purpose", None):
            with self.subTest(agent_type=agent_type):
                self.assertPassed(run_entry(hook_input(
                    "Bash", {"command": "git log -3"}, agent_type)))
                self.assertPassed(run_entry(hook_input(
                    "Read", {"file_path": "/Users/someone/.claude/projects/repo/a.jsonl"},
                    agent_type)))


class ForegroundAgentsTest(unittest.TestCase):
    """writ's own agents run in the foreground, so the caller gets a finished work back."""

    def run_start(self, tool_input, agent_type=None):
        return run_entry(hook_input("Agent", tool_input, agent_type))

    def test_given_writ_agent_started_in_background_when_hook_runs_then_moved_to_foreground(self):
        for agent in ("writ:generator", "writ:first-user"):
            with self.subTest(agent=agent):
                tool_input = {"description": "write", "prompt": "Write docs/x.md",
                              "subagent_type": agent, "run_in_background": True}
                result = self.run_start(tool_input)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)["hookSpecificOutput"]
                self.assertEqual(output["hookEventName"], "PreToolUse")
                self.assertEqual(output["permissionDecision"], "allow")
                self.assertEqual(output["updatedInput"], dict(tool_input, run_in_background=False))

    def test_given_writ_agent_started_without_the_field_when_hook_runs_then_set_to_foreground(self):
        result = self.run_start({"prompt": "Use docs/x.md", "subagent_type": "writ:first-user"},
                                "general-purpose")
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["updatedInput"],
                         {"prompt": "Use docs/x.md", "subagent_type": "writ:first-user",
                          "run_in_background": False})

    def test_given_other_agent_or_writ_agent_in_foreground_when_hook_runs_then_left_as_it_is(self):
        for tool_input in ({"prompt": "hi", "subagent_type": "general-purpose", "run_in_background": True},
                           {"prompt": "hi", "subagent_type": "writ:generator", "run_in_background": False}):
            with self.subTest(tool_input=tool_input):
                result = self.run_start(tool_input)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "")


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

    def test_given_no_python_when_first_user_calls_a_tool_then_blocked_with_install_message(self):
        for stdin in (hook_input("Read", {"file_path": "/Users/someone/repo/README.md"}),
                      hook_input("Bash", {"command": "ls"}).replace('": "', '":"')):
            with self.subTest(stdin=stdin[:40]):
                result = self.run_without_python(stdin)
                self.assertEqual(result.returncode, 2)
                self.assertIn("install Python 3.9 or later", result.stderr)

    def test_given_no_python_when_writ_agent_is_started_then_blocked_with_install_message(self):
        for stdin in (hook_input("Agent", {"prompt": "p", "subagent_type": "writ:generator"}, None),
                      hook_input("Agent", {"prompt": "p", "subagent_type": "writ:first-user"},
                                 None).replace('": "', '":"')):
            with self.subTest(stdin=stdin[-60:]):
                result = self.run_without_python(stdin)
                self.assertEqual(result.returncode, 2)
                self.assertIn("install Python 3.9 or later", result.stderr)

    def test_given_no_python_when_other_agent_calls_a_tool_then_passes(self):
        result = self.run_without_python(hook_input(
            "Bash", {"command": "echo agent_type writ:first-user"}, "general-purpose"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_given_python_on_path_when_first_user_runs_git_log_then_entry_blocks(self):
        env = {"PATH": os.path.dirname(sys.executable) + os.pathsep + self.bin,
               "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT}
        result = subprocess.run(["/bin/sh", "-c", self.command],
                                input=hook_input("Bash", {"command": "git log"}),
                                env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("first user does not read how the work was made", result.stderr)


if __name__ == "__main__":
    unittest.main()
