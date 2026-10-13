import contextlib
import io
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

from helpers import ROOT, Repo, run, started

import pretooluse
import stop


def hook(entry, repo, **data):
    """Runs a hook entry as Claude Code does; returns its exit code and what it told Claude."""
    data.setdefault("cwd", repo.path)
    data.setdefault("session_id", "s1")
    err = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(json.dumps(data))), contextlib.redirect_stderr(err):
        code = entry.main()
    return code, err.getvalue()


AIM = "a new teammate can start work alone"


def call(repo, agent, prompt, session="s1"):
    return hook(pretooluse, repo, session_id=session, hook_event_name="PreToolUse", tool_name="Agent",
                tool_input={"subagent_type": agent, "prompt": prompt, "description": "x"})


class AgentCalled(unittest.TestCase):
    """The orchestrator hands an agent of turn only the brief the script wrote for it."""

    def setUp(self):
        self.repo = Repo()
        started(self.repo)
        run(self.repo, "aim", ".turn/out", "1", AIM)
        self.repo.write(".turn/out/1/note.md", "# Note\n")

    def tearDown(self):
        self.repo.close()

    def test_an_agent_handed_its_brief_is_called(self):
        # Given: the generator's brief made
        _, out = run(self.repo, "brief", ".turn/out", "1", "generator")
        for name, path in (("from the top", out.strip()), ("in full", os.path.join(self.repo.path, out.strip()))):
            with self.subTest(name):
                # When: the orchestrator calls the generator with the brief's path
                code, _ = call(self.repo, "turn:generator", path)
                # Then: the call goes on
                self.assertEqual(code, 0)

    def test_an_agent_handed_anything_but_its_brief_is_stopped_saying_which_step(self):
        cases = [("words of its own", "turn:generator", "Write the README.", "step 4"),
                 ("a brief not made", "turn:first-user", ".turn/out/1/first-user-brief.json", "step 9"),
                 ("the evaluator", "turn:evaluator", "read it", "step 10"),
                 ("the learner", "turn:learner", "learn", "step 12")]
        for name, agent, prompt, step in cases:
            with self.subTest(name):
                # Given: an open run with no brief made for the agent
                # When: the orchestrator calls the agent with something else
                code, said = call(self.repo, agent, prompt)
                # Then: the call is stopped, naming the step and the command that makes the brief
                self.assertEqual(code, 2)
                self.assertIn(f"turn: {step}:", said)
                self.assertIn(f"brief .turn/out 1 {agent[5:]}", said)

    def test_the_entry_run_as_claude_code_runs_it_stops_a_call_without_its_brief(self):
        # Given: the hook's entry file, and an open run
        entry = os.path.join(ROOT, "turn", "hooks", "pretooluse.py")
        data = {"cwd": self.repo.path, "session_id": "s1", "hook_event_name": "PreToolUse",
                "tool_name": "Agent", "tool_input": {"subagent_type": "turn:generator", "prompt": "go"}}
        # When: Claude Code runs it on the call
        done = subprocess.run([sys.executable, entry], input=json.dumps(data), capture_output=True, text=True)
        # Then: it stops the call
        self.assertEqual(done.returncode, 2)
        self.assertIn("step 4", done.stderr)

    def test_nothing_outside_the_run_is_stopped(self):
        cases = [("another session", "turn:generator", "Agent", "s2"),
                 ("an agent not of turn", "other:writer", "Agent", "s1"),
                 ("another tool", "turn:generator", "Bash", "s1")]
        for name, agent, tool, session in cases:
            with self.subTest(name):
                # Given: an open run, and a call outside what the check covers
                # When: the call is made
                code, _ = hook(pretooluse, self.repo, session_id=session, hook_event_name="PreToolUse",
                               tool_name=tool, tool_input={"subagent_type": agent, "prompt": "go"})
                # Then: it goes on
                self.assertEqual(code, 0)


class Stopping(unittest.TestCase):
    """The orchestrator ends a run only through the step that returns the work and the CCS."""

    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_stopping_with_the_run_open_is_stopped_once_saying_the_last_step(self):
        # Given: an open run
        started(self.repo)
        # When: the orchestrator stops
        code, said = hook(stop, self.repo, hook_event_name="Stop", stop_hook_active=False)
        # Then: it is kept at work, told the last step
        self.assertEqual(code, 2)
        self.assertIn("turn: step 14:", said)
        self.assertIn("end .turn/out", said)
        # When: it stops again after being told
        code, _ = hook(stop, self.repo, hook_event_name="Stop", stop_hook_active=True)
        # Then: it is let stop, so it is never held in a loop
        self.assertEqual(code, 0)

    def test_stopping_outside_an_open_run_goes_on(self):
        cases = [("no run", False, "s1"), ("another session's run", True, "s2")]
        for name, open_run, session in cases:
            with self.subTest(name):
                # Given: no run, or a run of another session
                if open_run:
                    started(self.repo)
                # When: Claude stops
                code, _ = hook(stop, self.repo, session_id=session, hook_event_name="Stop",
                               stop_hook_active=False)
                # Then: it goes on
                self.assertEqual(code, 0)

    def test_the_entry_run_as_claude_code_runs_it_keeps_an_open_run_going(self):
        # Given: the hook's entry file, and an open run
        started(self.repo)
        entry = os.path.join(ROOT, "turn", "hooks", "stop.py")
        data = {"cwd": self.repo.path, "session_id": "s1", "hook_event_name": "Stop", "stop_hook_active": False}
        # When: Claude Code runs it as the orchestrator stops
        done = subprocess.run([sys.executable, entry], input=json.dumps(data), capture_output=True, text=True)
        # Then: it keeps it at work
        self.assertEqual(done.returncode, 2)
        self.assertIn("step 14", done.stderr)


if __name__ == "__main__":
    unittest.main()
