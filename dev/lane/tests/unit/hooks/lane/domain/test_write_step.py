"""write_step: a lane of the trace kind, whose step the subagent has done once it made an output the
lane names in this start, by Write, Edit or NotebookEdit, a file under it where it's a folder."""

import unittest
from typing import Any

import helpers
from lanes import write_step


class TestWriteStep(helpers.PluginTest):
    def done(self, run: list) -> Any:
        """What a subagent did whose calls of this start are those given."""
        return helpers.did(self.base, self.plugin, run, run)

    def test_a_write_of_an_output_or_under_one_is_its_trace(self):
        for tool, path in (("Write", "notes.md"), ("Edit", "out/a.md"), ("Write", "notes.md")):
            with self.subTest(tool=tool, path=path):
                # Given: the lane taking notes.md and the folder out, and a write of one
                given = {"output": ["notes.md", "out"]}
                done = self.done([helpers.kept_call(tool, file_path=path)])
                # When: the guard checks the step
                # Then: nothing is missing, and the call is its trace
                self.assertEqual(write_step.missing(given, done), "")
                self.assertTrue(write_step.traces(tool, path, given, done))

    def test_a_write_of_another_file_or_a_read_is_no_trace(self):
        for tool, path in (("Write", "outer.md"), ("Read", "notes.md")):
            with self.subTest(tool=tool, path=path):
                # Given: the lane taking notes.md and the folder out
                given = {"output": ["notes.md", "out"]}
                done = self.done([helpers.kept_call(tool, file_path=path)])
                # When: the guard checks the step after a write of another file, or a read
                # Then: each output is missing, and the call is no trace
                missing = "`notes.md` or `out` not made"
                self.assertEqual(write_step.missing(given, done), missing)
                self.assertFalse(write_step.traces(tool, path, given, done))

    def test_a_path_in_the_plugin_is_named_by_its_folder(self):
        # Given: the lane taking a file of the plugin, and a write of it by its full path
        given = {"output": ["${CLAUDE_PLUGIN_ROOT}/notes.md"]}
        path = f"{self.plugin}/notes.md"
        done = self.done([helpers.kept_call("Write", file_path=path)])
        # When: the guard checks the step
        # Then: nothing is missing
        self.assertEqual(write_step.missing(given, done), "")


if __name__ == "__main__":
    unittest.main()
