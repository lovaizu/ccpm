"""scripts/starts.py, the command the role before a step runs: each run's values on a line of its
own, as up starts each run with them, giving 0; or why it cannot, giving 2."""

import contextlib
import io
import json
import runpy
import unittest
from unittest import mock

import helpers
from helpers import starts

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/starts.py <run>"
    " generator|evaluator|refactorer|proofreader\n"
)


class TestMain(helpers.RunTest):
    def ran(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = starts.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_prints_each_run_s_values_on_a_line_of_its_own(self):
        self.lay()
        code, out, err = self.ran(self.folder, "evaluator")
        lines = out.splitlines()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(lines[0], "Runs of turn:evaluator, each started with its line:")
        self.assertEqual(
            [json.loads(line) for line in lines[1:]], helpers.runs.runs(self.folder, "evaluator")
        )

    def test_a_value_beyond_ascii_is_printed_as_it_is(self):
        made = helpers.run()
        made["work.json"]["commands"] = ["echo caf\u00e9"]
        self.lay(made)
        self.assertIn('"echo caf\u00e9"', self.ran(self.folder, "refactorer")[1])

    def test_a_run_it_cannot_read_gives_2_and_why(self):
        self.assertEqual(
            self.ran(self.folder, "refactorer"),
            (
                2,
                "",
                (
                    f"starts.py: could not give the runs of refactorer: there is no file"
                    f" {self.folder}/work.json\n"
                ),
            ),
        )

    def test_a_command_it_does_not_take_gives_2_and_its_usage(self):
        for argv in ((), (self.folder,), (self.folder, "generator", "x")):
            with self.subTest(argv=argv):
                self.assertEqual(self.ran(*argv), (2, "", USAGE))

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        self.lay()
        with (
            mock.patch.object(starts.sys, "argv", ["starts.py", self.folder, "refactorer"]),
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit) as end,
        ):
            runpy.run_path(starts.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
