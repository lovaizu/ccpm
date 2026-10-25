"""read_only: a call that reads anything but the inputs the lane takes is a drift, by the Read and
Grep tools and by the shell's commands that print what they read; every other call is not. Laid,
it lets the subagent read the form each in_form lane of its own names, too."""

import json
import os
import unittest

import helpers
from helpers import NO_PLUGIN, read_only, testing
from test_guard import GuardTest

TAKES = ["in.md"]


class ReadOnlyTest(testing.FolderTest):
    """A test whose calls are made in `base`, where the guard stands as it reads them."""

    def drifts(self, tool, given, takes=TAKES):
        """Whether the call of the tool with the input drifts from read_only taking the inputs."""
        made = helpers.acted(tool, given, self.base)
        return read_only.drifts(made, takes, NO_PLUGIN)

    def at(self, name):
        """The whole path of the name in `base`."""
        return os.path.join(self.base, name)


class TestDrift(ReadOnlyTest):
    def test_a_read_of_another_file_drifts(self):
        for tool, given in (
            ("Read", {"file_path": self.at("notes.md")}),
            ("Bash", {"command": "cat in.md notes.md"}),
            ("Bash", {"command": "sed -n '1,5p' notes.md"}),
            ("Grep", {"pattern": "x", "path": "notes.md"}),
        ):
            with self.subTest(tool=tool, given=given):
                # Given: a call reading a file other than the input, by a tool or a command
                # When: read_only reads it
                # Then: it is a drift
                self.assertTrue(self.drifts(tool, given))

    def test_a_search_of_the_folder_holding_the_input_drifts(self):
        # Given: a Grep call naming no path, which searches the folder it runs in
        # When: read_only reads it
        # Then: it is a drift, as it reads more than the input
        self.assertTrue(self.drifts("Grep", {"pattern": "x"}))


class TestLetThrough(ReadOnlyTest):
    def test_a_read_of_the_input_is_no_drift(self):
        for tool, given in (
            ("Read", {"file_path": self.at("in.md")}),
            ("Read", {"file_path": "in.md", "offset": 10}),
            ("Bash", {"command": "head -n 5 in.md && grep x in.md"}),
            ("Bash", {"command": "cd sub && cat ../in.md"}),
        ):
            with self.subTest(tool=tool, given=given):
                # Given: a call reading the input by its whole path or its path from the folder
                # When: read_only reads it
                # Then: it is no drift
                self.assertFalse(self.drifts(tool, given))

    def test_a_read_of_a_file_in_an_input_folder_is_no_drift(self):
        # Given: a lane taking a folder, and a call reading a file in it
        # When: read_only reads it
        # Then: it is no drift
        self.assertFalse(self.drifts("Read", {"file_path": self.at("docs/a.md")}, ["docs/"]))

    def test_a_read_of_any_input_taken_is_no_drift(self):
        # Given: a lane taking two inputs, and a call reading the second
        # When: read_only reads it
        # Then: it is no drift
        self.assertFalse(self.drifts("Bash", {"command": "cat b.md"}, ["in.md", "b.md"]))

    def test_a_call_reading_no_file_is_no_drift(self):
        for tool, given in (
            ("Bash", {"command": "ls && git status"}),
            ("Bash", {"command": 'cat "$f"'}),
            ("Write", {"file_path": self.at("notes.md"), "content": "x"}),
        ):
            with self.subTest(tool=tool, given=given):
                # Given: a call that reads no file, or none the words settle
                # When: read_only reads it
                # Then: it is no drift
                self.assertFalse(self.drifts(tool, given))


class TestGuard(GuardTest):
    """read_only and in_form laid on changelog-writer, with write_only and hands_off beside them on
    the step of in_form, run by the guard as Claude Code runs it."""

    LAID = (
        (1, "read_only", TAKES),
        (3, "in_form", ["entry.json", "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"]),
        (3, "write_only", ["entry.json"]),
        (3, "hands_off", ["git push"]),
    )

    def reading(self, name):
        """The guard on changelog-writer reading the file of the plugin with Read."""
        event = self.called("Read", {"file_path": os.path.join(self.plugin, name)})
        return self.guard(json.dumps(event))

    def test_a_read_of_the_form_its_in_form_names_is_let_through(self):
        # Given: read_only and in_form laid on changelog-writer
        # When: it reads the form its in_form names, a file of the plugin
        # Then: the call goes on, nothing said
        self.assertEqual(self.reading("forms/entry.json"), ("", ""))

    def test_a_read_of_another_file_of_the_plugin_is_stopped(self):
        # Given: read_only and in_form laid on changelog-writer
        # When: it reads a file of the plugin no lane of its names, such as a form another
        # subagent's in_form names
        for name in ("agents/writer.md", "forms/other.json"):
            with self.subTest(name=name):
                # Then: the call is stopped with read_only's sentence
                expected = ("told", "notes: Read only `in.md`.")
                self.assertEqual(self.reading(name), expected)

    def test_the_form_is_let_through_to_read_only_alone(self):
        # Given: read_only and in_form laid on changelog-writer, and write_only on the step of
        # in_form
        form = os.path.join(self.plugin, "forms", "entry.json")
        event = self.called("Write", {"file_path": form, "content": "{}"})
        # When: it writes the form its in_form names
        # Then: the call is stopped with write_only's sentence, as the form is no output of it
        expected = ("told", "notes: Write only `entry.json`.")
        self.assertEqual(self.guard(json.dumps(event)), expected)


if __name__ == "__main__":
    unittest.main()
