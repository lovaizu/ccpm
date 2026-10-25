"""The tests of rn's command line: each option a subcommand needs, and rn run as the command the
orchestrator runs."""

from __future__ import annotations

import contextlib
import io
import os
import re
import runpy
import sys
import unittest
from unittest import mock

from helpers import (
    SCRIPTS,
    RepoTest,
    rn,
    steered,
)


class UsageTest(RepoTest):
    def test_each_option_needed_left_out_stops_with_the_usage(self):
        start = ["start", "add-login", "--title", "t", "--artifact-language", "a"]
        given = {
            "start": start + ["--conversation-language", "c", "--message", "m"],
            "state": ["state", "--message", "m"],
            "decide": ["decide", "t1.1", "--title", "t", "--says", "s", "--message", "m"],
            "answer": ["answer", "approved", "--message", "m"],
        }
        for name, argv in given.items():
            for k in (k for k, arg in enumerate(argv) if arg.startswith("--")):
                with self.subTest(argv=argv, left=argv[k]):
                    # Given: a branch with a session.
                    self.session(steered(signoff="plan"))
                    # When: the orchestrator runs the subcommand without the option.
                    # Then: rn says it is required.
                    self.assertIn(
                        f"rn: the following arguments are required: {argv[k]}; give it as rn.py"
                        f" {name}",
                        self.stopped(*argv[:k], *argv[k + 2 :]),
                    )


class StepsTest(unittest.TestCase):
    def test_each_next_rn_sets_names_a_step_of_rn_up(self):
        # Given: each Next rn sets itself, and the steps of /rn:up, in its SKILL.md and the files
        # of its stages.
        folder = os.path.join(SCRIPTS, "..", "skills", "up")
        steps = set()
        for name in os.listdir(folder):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                steps.update(re.findall(r"^ ?([0-9]+)\. ", f.read(), re.MULTILINE))
        nexts = [rn.STARTED, rn.FEEDBACK, rn.WAITING]
        nexts += list(rn.APPROVED_NEXT.values()) + list(rn.STAGED.values())
        # When: the step each names is read.
        named = [re.match(r"Step ([0-9]+) of /rn:up", n) for n in nexts]
        # Then: each but the session finished names a step of /rn:up that is there.
        self.assertEqual(
            [m[1] in steps if m else n for m, n in zip(named, nexts)],
            [True] * 8 + [rn.STAGED["finished"]],
        )


class CommandTest(RepoTest):
    def test_the_command_prints_and_exits_1_on_a_stop(self):
        # Given: rn.py run as a command, as the orchestrator runs it, with the plugin's own
        # checklists; run in this process, so that the coverage of the test run counts it.
        script = os.path.join(SCRIPTS, "rn.py")
        out = io.StringIO()
        # When: it is asked for a kind with no checklist.
        argv = mock.patch.object(sys, "argv", [script, "checklists", "no-such-kind"])
        with argv, contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as done:
            runpy.run_path(script, run_name="__main__")
        # Then: it exits 1, saying what went wrong.
        said = "no checklist for the kind no-such-kind" in out.getvalue()
        self.assertEqual((done.exception.code, said), (1, True))

    def test_no_subcommand_stops_with_the_usage(self):
        # Given: rn run with no subcommand.
        # When: it runs.
        # Then: it says a subcommand is required, and names them.
        self.assertIn(
            "required: subcommand; give it as rn.py [-h]"
            " {session,start,state,decide,ccs,proposal,answer,checklists,decisions,learnings}",
            self.stopped(),
        )


if __name__ == "__main__":
    unittest.main()
