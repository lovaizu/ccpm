"""scripts/tree.py, the commands designer runs on a run: check, whether the design tree asks the
template's questions and the work's parts and remake hold, giving 0, 1 or 2; and parts, the
decisions split into the parts written into work.json."""

import contextlib
import io
import runpy
import unittest
from unittest import mock

import helpers
from helpers import tree


class TreeTest(helpers.RunTest):
    def ran(self, *argv):
        """The exit code tree.py gives on the words, and what it prints and prints as errors."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tree.main(list(argv))
        return code, out.getvalue(), err.getvalue()


class TestCheck(TreeTest):
    def test_a_run_that_holds_gives_0(self):
        self.lay()
        self.assertEqual(
            self.ran("check", self.folder),
            (
                0,
                (
                    f"tree.py: {self.folder} holds: the tree asks each question of the template"
                    " as it asks it, and the work's parts and the remake hold.\n"
                ),
                "",
            ),
        )

    def test_a_run_that_does_not_hold_gives_1_and_each_fault(self):
        made = helpers.run()
        made["work.json"]["parts"][0]["paths"] = []
        made["work.json"]["paths"] = []
        self.lay(made)
        self.assertEqual(
            self.ran("check", self.folder),
            (
                1,
                (
                    f"tree.py: {self.folder} does not hold:\n- the work has no paths\n- P1 has no"
                    " paths\n"
                ),
                "",
            ),
        )

    def test_a_run_that_cannot_be_checked_gives_2_and_why(self):
        self.assertEqual(
            self.ran("check", self.folder),
            (
                2,
                "",
                (
                    f"tree.py: could not check {self.folder}: there is no file"
                    f" {self.folder}/design-tree.json\n"
                ),
            ),
        )


class TestParts(TreeTest):
    def test_writes_the_parts_into_work_json_and_says_them(self):
        made = helpers.run()
        made["design-tree.json"]["decisions"].append(helpers.decision("D4", [helpers.question(3)]))
        made["work.json"] = {
            "paths": ["a.md", "b.md"],
            "commands": [],
            "parts": [{"id": "P1", "decisions": ["D1"], "paths": ["a.md"]}],
        }
        self.lay(made)
        self.assertEqual(
            self.ran("parts", self.folder),
            (
                0,
                (
                    f"tree.py: wrote the parts into {self.folder}/work.json: P1 D1; P2 D2, D3; P3"
                    " D4. Give each part its paths, and join two parts whose files meet.\n"
                ),
                "",
            ),
        )
        self.assertEqual(
            [p["decisions"] for p in self.read_json(f"{self.folder}/work.json")["parts"]],
            [["D1"], ["D2", "D3"], ["D4"]],
        )

    def test_a_run_with_no_work_json_yet_gets_one(self):
        made = helpers.run()
        del made["work.json"]
        self.lay(made)
        self.assertEqual(self.ran("parts", self.folder)[0], 0)
        self.assertEqual(
            self.read_json(f"{self.folder}/work.json"),
            {
                "paths": [],
                "commands": [],
                "parts": [
                    {"id": "P1", "decisions": ["D1"], "paths": []},
                    {"id": "P2", "decisions": ["D2", "D3"], "paths": []},
                ],
            },
        )

    def test_a_tree_that_cannot_be_read_gives_2(self):
        code, out, err = self.ran("parts", self.folder)
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith(f"tree.py: could not split {self.folder}: there is no file"))


class TestUsage(TreeTest):
    def test_a_command_it_does_not_take_gives_2_and_its_usage(self):
        for argv in ((), ("check",), ("print", "x"), ("check", "x", "y")):
            with self.subTest(argv=argv):
                self.assertEqual(
                    self.ran(*argv),
                    (
                        2,
                        "",
                        "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py check|parts <run>\n",
                    ),
                )

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        self.lay()
        with (
            mock.patch.object(tree.sys, "argv", ["tree.py", "check", self.folder]),
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit) as end,
        ):
            runpy.run_path(tree.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
