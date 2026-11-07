"""scripts/throwaway.py, what the generator runs once it has made the deliverable: 0 with the try
record's path, 1 with what's wrong, 2 with why it can't read the run, and 2 with its usage."""

from __future__ import annotations

import os
import runpy
import sys
from unittest import mock

import helpers
from helpers import RUN, ran, runs, throwaway

from unit.domain.test_starts import made

CONTENT = os.path.join(RUN, "turns", "01-readme-md", "01")


class Throwaway(helpers.RunTest):
    def test_the_try_record_is_written_and_named(self):
        self.lays(helpers.walkthrough())
        self.write_json(os.path.join(CONTENT, runs.MADE), made(commands=["true"]))
        code, out, err = ran(throwaway, RUN)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(
            out,
            f"throwaway.py: the try record is {CONTENT}/throwaway.txt. Read it whole before you"
            " judge.\n",
        )

    def test_whats_wrong_gives_1_and_what_it_cant_read_2(self):
        self.lays(helpers.walkthrough())
        code, _, err = ran(throwaway, RUN)
        self.assertEqual(code, 1)
        self.assertIn("throwaway.py: ", err)
        self.write(runs.tree_path(RUN), "{")
        code, _, err = ran(throwaway, RUN)
        self.assertEqual(code, 2)
        self.assertIn("throwaway.py: can't try the commands: ", err)

    def test_its_usage(self):
        self.assertEqual(
            ran(throwaway),
            (2, "", "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py <run>\n"),
        )

    def test_run_as_a_command_it_gives_its_code(self):
        argv = [os.path.join(helpers.SCRIPTS, "throwaway.py")]
        with mock.patch.object(sys, "argv", argv), self.assertRaises(SystemExit) as stop:
            runpy.run_path(argv[0], run_name="__main__")
        self.assertEqual(stop.exception.code, 2)

    def test_two_runs_given_are_its_usage(self):
        self.assertEqual(ran(throwaway, RUN, RUN)[0], 2)
