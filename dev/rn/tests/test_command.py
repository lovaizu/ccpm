"""The tests of rn's command line: each option a subcommand needs, and rn run as the command the
orchestrator runs."""

from __future__ import annotations

import contextlib
import io
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from helpers import (
    SCRIPTS,
    RepoTest,
    proposal,
    session,
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
        # Given: each Next rn sets itself, and the steps of /rn:up, in orchestrator.md and the files
        # of its stages.
        folder = os.path.join(SCRIPTS, "..", "prompts")
        steps = set()
        for name in os.listdir(folder):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                steps.update(re.findall(r"^ ?([0-9]+)\. ", f.read(), re.MULTILINE))
        nexts = [session.STARTED, proposal.FEEDBACK, proposal.WAITING]
        nexts += list(proposal.APPROVED_NEXT.values()) + list(session.STAGED.values())
        # When: the step each names is read.
        named = [re.match(r"Step ([0-9]+) of /rn:up", n) for n in nexts]
        # Then: each but the session finished names a step of /rn:up that is there.
        self.assertEqual(
            [m[1] in steps if m else n for m, n in zip(named, nexts)],
            [True] * 8 + [session.STAGED["finished"]],
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
            " {session,start,state,decide,ccs,check,proposal,answer,checklists,decisions,"
            "learnings,history,search}",
            self.stopped(),
        )


if __name__ == "__main__":
    unittest.main()


class InstalledTest(unittest.TestCase):
    def test_rn_copied_as_installing_copies_it_runs(self):
        # Given: rn copied as installing copies it, each link given the file it points to, so the
        # code rn takes from turn and lane through a link finds only what rn carries.
        with tempfile.TemporaryDirectory() as folder:
            copy = os.path.join(folder, "rn")
            shutil.copytree(os.path.dirname(SCRIPTS), copy)
            # When: the orchestrator runs rn.
            ran = subprocess.run(
                [sys.executable, os.path.join(copy, "scripts", "rn.py"), "--help"],
                capture_output=True,
                text=True,
                check=False,
            )
        # Then: it runs.
        self.assertEqual((ran.returncode, ran.stderr), (0, ""))
