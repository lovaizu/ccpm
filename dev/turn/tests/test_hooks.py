import contextlib
import io
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

from helpers import ROOT, Repo, fill, run, started

import subagentstop


def hook(repo, **data):
    """Runs the SubagentStop hook as Claude Code does; returns its exit code and what it told the agent."""
    data.setdefault("cwd", repo.path)
    err = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(json.dumps(data))), contextlib.redirect_stderr(err):
        code = subagentstop.main()
    return code, err.getvalue()


class HandBack(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], "# Note\n\nRun make.\n")

    def tearDown(self):
        self.repo.close()

    def hand_back(self, agent, session="s1"):
        return hook(self.repo, session_id=session, hook_event_name="SubagentStop", agent_type=agent)

    def test_an_agent_handing_back_with_its_form_unfilled_is_kept_at_it(self):
        # Given: the generator's form left empty in an open run
        # When: the generator hands back
        code, said = self.hand_back("turn:generator")
        # Then: it is stopped, told which step and what is missing
        self.assertEqual(code, 2)
        self.assertIn("turn: fill your form before handing back", said)
        self.assertIn("note B-1: lines are not given", said)

    def test_an_agent_handing_back_with_its_form_filled_goes_on(self):
        # Given: the first user's form filled for every item
        fill(self.repo, self.got["forms"]["first-user"], {
            "note B-1": {"took": "run make", "lines": "3"}})
        # When: the first user hands back
        code, _ = self.hand_back("turn:first-user")
        # Then: it goes on
        self.assertEqual(code, 0)

    def test_an_agent_handing_back_before_the_work_is_written_is_told_so(self):
        # Given: the work not written
        os.remove(os.path.join(self.repo.path, self.got["work"]))
        # When: the generator hands back
        code, said = self.hand_back("turn:generator")
        # Then: it is stopped, told the work is missing
        self.assertEqual(code, 2)
        self.assertIn(".turn/out/1/note.md is not written", said)

    def test_the_hook_run_as_claude_code_runs_it_stops_an_unfilled_form(self):
        # Given: the hook's entry file, and an empty form in an open run
        entry = os.path.join(ROOT, "turn", "hooks", "subagentstop.py")
        data = {"cwd": self.repo.path, "session_id": "s1", "hook_event_name": "SubagentStop",
                "agent_type": "turn:generator"}
        # When: Claude Code runs it on a hand-back
        done = subprocess.run([sys.executable, entry], input=json.dumps(data), capture_output=True,
                              text=True)
        # Then: it stops the call with what is missing
        self.assertEqual(done.returncode, 2)
        self.assertIn("note B-1: lines are not given", done.stderr)

    def test_nothing_outside_the_run_is_stopped(self):
        cases = [
            ("another session", "turn:generator", "s2", "SubagentStop"),
            ("an agent not of turn", "other:writer", "s1", "SubagentStop"),
            ("an agent of turn with no form", "turn:learner", "s1", "SubagentStop"),
            ("another event", "turn:generator", "s1", "Stop"),
        ]
        for name, agent, session, event in cases:
            with self.subTest(name):
                # Given: an empty form, and a call from outside what the check covers
                # When: the call is made
                code, _ = hook(self.repo, session_id=session, hook_event_name=event, agent_type=agent)
                # Then: it goes on
                self.assertEqual(code, 0)

    def test_nothing_is_stopped_once_the_run_has_ended(self):
        # Given: a run that has ended
        fill(self.repo, self.got["forms"]["orchestrator"], {
            "note B-1": {"met": True, "lines": "3", "note": "x"},
            "note F-1": {"met": True, "lines": "1", "note": "x"}})
        self.assertEqual(run(self.repo, "end", ".turn/out", "1")[0], 0)
        # When: an agent named like turn's hands back with an empty form
        code, _ = self.hand_back("turn:generator")
        # Then: it goes on
        self.assertEqual(code, 0)

    def test_nothing_is_stopped_in_a_repository_with_no_run(self):
        # Given: a repository where turn has never run
        other = Repo()
        # When: an agent named like turn's hands back
        code, _ = hook(other, session_id="s1", hook_event_name="SubagentStop", agent_type="turn:generator")
        # Then: it goes on
        self.assertEqual(code, 0)
        other.close()


if __name__ == "__main__":
    unittest.main()
