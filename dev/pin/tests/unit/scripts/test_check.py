"""check.py, the command a pinner runs: the path read, and the tree found to hold, not to hold, or
not to be checkable, each with what it prints and the exit code a script reads."""

import contextlib
import io
import unittest

import helpers
from helpers import check, decision, made


class TestMain(helpers.testing.FolderTest):
    def ran(self, *argv: str) -> tuple:
        """The exit code check.py gives on the words, and what it prints to its output and to its
        error output."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = check.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_a_tree_that_holds_gives_0_and_the_decisions_ready(self):
        # Given: a tree that holds, D1 decided and D2 open on it
        self.write_json(
            "t.json",
            made(helpers.settled("D1"), decision("D2", builds_on=["D1"]), decision("D3")),
        )
        # When: check.py is run on it
        # Then: it says the tree holds and which decisions can be decided now, and gives 0
        self.assertEqual(
            self.ran("t.json"),
            (
                0,
                (
                    "check.py: t.json holds: every question is served, every decision reaches the"
                    " goal, and each decision comes after the ones it builds on.\n"
                    "Open to decide now: D2, D3.\n"
                ),
                "",
            ),
        )

    def test_a_tree_with_every_decision_decided_says_none_is_open(self):
        # Given: the walkthrough's tree
        self.write_json("t.json", helpers.walkthrough())
        # When: check.py is run on it
        code, out, _ = self.ran("t.json")
        # Then: it gives 0, and says no decision is open
        self.assertEqual(code, 0)
        self.assertTrue(out.endswith("\nNo decision is open.\n"))

    def test_a_tree_that_does_not_hold_gives_1_and_each_problem(self):
        # Given: a tree with a question no decision serves
        self.write_json("t.json", made(decision("D1"), questions=("Q1", "Q2")))
        # When: check.py is run on it
        # Then: it names each problem, and gives 1
        self.assertEqual(
            self.ran("t.json"),
            (1, "check.py: t.json does not hold:\n- Q2 is served by no decision.\n", ""),
        )

    def test_a_tree_that_cannot_be_read_gives_2_and_why(self):
        # Given: no file at the path
        # When: check.py is run on it
        # Then: it says it could not check it and why, on its error output, and gives 2
        self.assertEqual(
            self.ran("gone.json"),
            (2, "", "check.py: could not check gone.json:\n- there is no file gone.json\n"),
        )

    def test_words_other_than_one_path_print_the_usage_and_give_2(self):
        for argv in ((), ("a.json", "b.json")):
            with self.subTest(argv=argv):
                # Given: no path, or two
                # When: check.py is run with them
                # Then: it prints how to run it, and gives 2
                self.assertEqual(self.ran(*argv), (2, "", check.USAGE + "\n"))


if __name__ == "__main__":
    unittest.main()
