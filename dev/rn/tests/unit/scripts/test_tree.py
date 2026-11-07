"""scripts/tree.py, what the main conversation and rn's roles run: each command by its name and its
arguments, 0 with what it printed, 1 with what's wrong, 2 with why it can't read what it needs, and
2 with its usage for a command it doesn't take."""

from __future__ import annotations

import json
import os
import runpy
import sys
from unittest import mock

import helpers
from helpers import GOAL, RUN, ran, runs, tree


class Commands(helpers.RunTest):
    def test_a_change_on_standard_input_then_the_planners_cut(self):
        self.lays(helpers.walkthrough("maker"))
        code, out, err = ran(tree, "change", stdin=json.dumps({"run": RUN}))
        self.assertEqual((code, err), (0, ""))
        self.assertIn(f"rn: the change for {RUN} is kept.", out)
        code, out, _ = ran(tree, "start", "planner")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.splitlines()[0])["run"], RUN)

    def test_each_command_of_the_main_conversation_and_the_planner(self):
        self.lays(helpers.walkthrough("maker"))
        self.assertIn("The goal, to confirm", ran(tree, "points")[1])
        self.assertIn("Picking up", ran(tree, "status")[1])
        path = self.edit({"grounds": "g", "nodes": [{"id": "goal", "decided": GOAL, "by": "user"}]})
        self.assertEqual(ran(tree, "write", RUN, path)[0], 0)
        self.assertEqual(ran(tree, "commit", RUN)[0], 1)
        self.assertEqual(ran(tree, "report", RUN)[0], 0)

    def test_whats_wrong_gives_1(self):
        code, out, err = ran(tree, "change", stdin="{")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("tree.py: the change is no JSON", err)

    def test_what_it_cant_read_gives_2(self):
        self.write(runs.tree_path(RUN), "{")
        code, _, err = ran(tree, "points")
        self.assertEqual(code, 2)
        self.assertIn("tree.py: can't points: ", err)

    def test_a_command_it_doesnt_take_gives_its_usage(self):
        for argv in ([], ["start"], ["unknown"], ["check"], ["write", RUN]):
            with self.subTest(argv=argv):
                code, out, err = ran(tree, *argv)
                self.assertEqual((code, out), (2, ""))
                self.assertTrue(
                    err.startswith("usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py change")
                )


class Check(helpers.RunTest):
    def test_a_tree_that_holds_one_out_of_order_and_one_it_cant_read(self):
        self.lays(helpers.walkthrough())
        path = runs.tree_path(RUN)
        self.assertEqual(ran(tree, "check", path), (0, f"tree.py: {path} holds.\n", ""))
        data = helpers.walkthrough()
        data["deliverables"].reverse()
        self.lays(data)
        code, _, err = ran(tree, "check", path)
        self.assertEqual(code, 1)
        self.assertEqual(
            err, f"tree.py: {path}: D1 takes README.md in its inputs, which comes later\n"
        )
        code, _, err = ran(tree, "check", "gone.json")
        self.assertEqual(code, 2)
        self.assertIn("tree.py: gone.json can't be checked: there is no file gone.json", err)


class Script(helpers.RunTest):
    def test_run_as_a_command_it_gives_its_code(self):
        argv = [os.path.join(helpers.SCRIPTS, "tree.py"), "status"]
        with mock.patch.object(sys, "argv", argv), self.assertRaises(SystemExit) as stop:
            runpy.run_path(argv[0], run_name="__main__")
        self.assertEqual(stop.exception.code, 1)


class Edges(helpers.RunTest):
    def test_a_command_like_check_or_check_with_more_words_is_no_check(self):
        for argv in (["change", "x"], ["check", "a", "b"]):
            with self.subTest(argv=argv):
                self.assertEqual(ran(tree, *argv)[0], 2)

    def test_what_it_cant_read_names_the_command(self):
        self.write(runs.tree_path(RUN), "{")
        code, _, err = ran(tree, "start", "generator")
        self.assertEqual(code, 2)
        self.assertIn("tree.py: can't start: ", err)
