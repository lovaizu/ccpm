"""The result script: a subagent's result taken where a route is from the subagent on it, exiting
with no error and nothing said; anything else refused with an error naming what is wrong and the
commands the subagent may end by."""

import io
import os
import runpy
import subprocess
import sys
import unittest
from unittest import mock

import helpers
from helpers import result


class ResultTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.route()

    def given(self, *argv: str) -> tuple:
        """The exit and what the result script says, run with the words in the plugin."""
        err = io.StringIO()
        return result.main(list(argv), err, self.plugin), err.getvalue()


class TestGiven(ResultTest):
    def test_a_result_of_a_route_exits_with_no_error_and_nothing_said(self):
        for argv in (("writer", "written"), ("reviewer", "more"), ("reviewer", "good")):
            with self.subTest(argv=argv):
                # Given: the routes laid
                # When: a subagent gives a result its routes are on
                # Then: it exits 0, saying nothing
                self.assertEqual(self.given(*argv), (0, ""))


class TestRefused(ResultTest):
    def test_a_result_no_route_is_on_is_refused_with_the_commands_to_end_by(self):
        # Given: the routes laid
        # When: writer gives `good`
        # Then: it exits 1, telling writer the sentence of its last step, as it reads it
        gives = f"python3 {self.plugin}/hooks/lane/result.py writer written"
        self.assertEqual(
            self.given("writer", "good"),
            (
                1,
                f"changelog: writer gives no `good`. End by running `{gives}`.{helpers.NOT_WORK}\n",
            ),
        )

    def test_a_subagent_no_route_is_from_is_refused(self):
        # Given: the routes laid
        # When: lead gives a result
        # Then: it is refused, as no route is from lead on a result
        self.assertEqual(
            self.given("lead", "done"), (1, "changelog: no route is from lead on a result.\n")
        )

    def test_words_not_a_subagent_and_a_result_are_refused_with_the_form(self):
        for argv in ((), ("writer",), ("writer", "written", "x")):
            with self.subTest(argv=argv):
                # Given: the routes laid
                # When: the script is run with no word, one, or three
                # Then: it is refused, showing the form a result is given in
                self.assertEqual(
                    self.given(*argv),
                    (
                        1,
                        (
                            f"changelog: give a result as `python3 {self.plugin}/hooks/lane/"
                            "result.py <subagent> <result>`.\n"
                        ),
                    ),
                )

    def test_lanes_json_that_cannot_be_read_is_an_error_naming_the_fix(self):
        # Given: hooks/lanes.json removed, and the manifest of no JSON
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        self.write(self.manifest(), "{")
        # When: writer gives `written`
        code, said = self.given("writer", "written")
        # Then: it exits 1, headed lane: as the plugin's name cannot be read, naming the fix
        self.assertEqual(code, 1)
        self.assertTrue(
            said.startswith(
                "lane: lane cannot check the lanes of writer: hooks/lanes.json is not there."
            ),
            said,
        )
        self.assertIn("`lay.py write`", said)


class TestRun(unittest.TestCase):
    def test_the_script_checks_the_result_alone_with_no_guard_and_no_port(self):
        # Given: lane's result script, as a step runs it, in a Python of its own
        script = os.path.join(helpers.CODE, "result.py")
        shown = "import sys; sys.argv = [sys.argv[0], 'w', 'x']; import runpy\n"
        shown += "try:\n    runpy.run_path(%r, run_name='__main__')\nexcept SystemExit:\n    pass\n"
        shown += "print(sorted({'guard', 'ports', 'called'} & set(sys.modules)))"
        # When: it is run
        done = subprocess.run(
            [sys.executable, "-c", shown % script], capture_output=True, text=True, check=True
        )
        # Then: it loads neither the guard, the calls kept nor the ports, as it checks the result
        # alone (dev/lane/architecture.md, Components)
        self.assertEqual(done.stdout.strip().splitlines()[-1], "[]")

    def test_the_script_run_as_a_command_finds_the_plugin_by_its_own_path(self):
        # Given: lane's own result script, in lane, which lays no routes in itself
        script = os.path.join(helpers.CODE, "result.py")
        err = io.StringIO()
        # When: it is run as a step writes it
        argv = mock.patch.object(sys, "argv", [script, "writer", "written"])
        with argv, mock.patch.object(sys, "stderr", err), self.assertRaises(SystemExit) as end:
            runpy.run_path(script, run_name="__main__")
        # Then: it reads lane as the plugin it lies in, and exits 1, finding no routes there
        self.assertEqual(end.exception.code, 1)
        self.assertTrue(
            err.getvalue().startswith("lane: lane cannot check the lanes of writer:"),
            err.getvalue(),
        )


class TestResults(helpers.PluginTest):
    def test_a_subagent_with_its_own_results_gives_each_of_them_alone(self):
        # Given: writer laid giving `asks` and `done`, no route laid
        self.lay_lanes([{"step": 2, "lanes": helpers.STEPS[0]["lanes"]}], results=["asks", "done"])
        err = io.StringIO()
        # When: it gives `asks`, `done` and `written`
        # Then: the first two exit 0, and the third is told the commands it ends by
        self.assertEqual(result.main(["writer", "asks"], err, self.plugin), 0)
        self.assertEqual(result.main(["writer", "done"], err, self.plugin), 0)
        self.assertEqual(result.main(["writer", "written"], err, self.plugin), 1)
        gives = f"python3 {self.plugin}/hooks/lane/result.py writer"
        self.assertEqual(
            err.getvalue(),
            f"changelog: writer gives no `written`. End by running `{gives} asks` or"
            f" `{gives} done`.{helpers.NOT_WORK}\n",
        )


class TestDone(helpers.PluginTest):
    def test_a_subagent_with_a_lane_of_the_end_and_no_route_gives_done(self):
        # Given: writer ending once CHANGELOG.md is made, no route laid
        self.lay_lanes([{"step": 3, "lanes": [{"lane": "end_when", "takes": ["CHANGELOG.md"]}]}])
        err = io.StringIO()
        # When: it gives `done`, and `written`
        # Then: the first exits 0, and the second is told the command it ends by
        self.assertEqual(result.main(["writer", "done"], err, self.plugin), 0)
        self.assertEqual(result.main(["writer", "written"], err, self.plugin), 1)
        gives = f"python3 {self.plugin}/hooks/lane/result.py writer done"
        self.assertEqual(
            err.getvalue(),
            f"changelog: writer gives no `written`. End by running `{gives}`.{helpers.NOT_WORK}\n",
        )


if __name__ == "__main__":
    unittest.main()
