"""run_step: a lane of the trace kind, whose step the subagent has done once a command it names came
back in this start, matched whole, each value the start's own."""

import unittest
from typing import Any

import helpers
from lanes import run_step


class TestRunStep(helpers.PluginTest):
    def done(self, run: list) -> Any:
        """What a subagent did whose calls of this start are those given, its values `file`."""
        found = helpers.did(self.base, self.plugin, run, run)
        return found._replace(values={"file": ["a.md"]})

    def test_a_command_named_that_came_back_is_its_trace(self):
        for command in ("make test", "check a.md"):
            with self.subTest(command=command):
                # Given: the lane taking `make test` or `check {file}`, and that command come back
                given = {"commands": ["make test", "check {file}"]}
                done = self.done([helpers.kept_call("Bash", command=command)])
                # When: the guard checks the step
                # Then: nothing is missing, and the call is its trace
                self.assertEqual(run_step.missing(given, done), "")
                self.assertTrue(run_step.traces("Bash", command, given, done))

    def test_another_command_or_tool_is_no_trace(self):
        for tool, value in (("Bash", "make"), ("Bash", "check b.md"), ("Read", "make test")):
            with self.subTest(tool=tool, value=value):
                # Given: the lane taking `make test` or `check {file}`, the start's file a.md
                given = {"commands": ["make test", "check {file}"]}
                done = self.done([helpers.kept_call(tool, command=value)])
                # When: the guard checks the step after a call of another command or tool
                # Then: each command is missing, and the call is no trace
                missing = "`make test` or `check {file}` not run"
                self.assertEqual(run_step.missing(given, done), missing)
                self.assertFalse(run_step.traces(tool, value, given, done))


if __name__ == "__main__":
    unittest.main()
