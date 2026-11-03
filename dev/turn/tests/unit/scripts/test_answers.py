"""scripts/answers.py, the command builder, evaluator, refactorer and proofreader run on their
answers file: 0 where every question they were given is answered and each line lies in the work,
1 with each fault, and 2 where it cannot check."""

import contextlib
import io
import runpy
import unittest
from unittest import mock

import helpers
from helpers import answers

USAGE = "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/answers.py check <run> <answers>\n"


class TestMain(helpers.RunTest):
    def ran(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = answers.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def setUp(self):
        super().setUp()
        self.lay()
        self.path = f"{self.folder}/verification/G1.json"

    def test_answers_that_hold_give_0(self):
        self.write_json(
            self.path, {"good": [{"question": "readme/Q1", "lines": ["README.md:1"]}], "more": []}
        )
        self.assertEqual(
            self.ran("check", self.folder, self.path),
            (0, f"answers.py: {self.path} answers each question it was given: readme/Q1.\n", ""),
        )

    def test_answers_that_do_not_hold_give_1_and_each_fault(self):
        self.write_json(self.path, {"good": [], "more": []})
        self.assertEqual(
            self.ran("check", self.folder, self.path),
            (1, f"answers.py: {self.path} does not hold:\n- readme/Q1 has no answer\n", ""),
        )

    def test_answers_that_cannot_be_checked_give_2_and_why(self):
        self.assertEqual(
            self.ran("check", self.folder, self.path),
            (2, "", f"answers.py: could not check {self.path}: there is no file {self.path}\n"),
        )

    def test_a_command_it_does_not_take_gives_2_and_its_usage(self):
        for argv in ((), ("check", self.folder), ("look", self.folder, self.path)):
            with self.subTest(argv=argv):
                self.assertEqual(self.ran(*argv), (2, "", USAGE))

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        self.write_json(
            self.path, {"good": [], "more": [{"question": "readme/Q1", "good_when": "w"}]}
        )
        with (
            mock.patch.object(answers.sys, "argv", ["answers.py", "check", self.folder, self.path]),
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit) as end,
        ):
            runpy.run_path(answers.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
