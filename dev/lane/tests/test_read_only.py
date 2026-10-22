"""read_only: a call that reads anything but the inputs the lane takes is a drift, by the Read and
Grep tools and by the shell's commands that print what they read; every other call is not."""

import os
import unittest

from helpers import call, read_only, testing

TAKES = ["in.md"]


class ReadOnlyTest(testing.FolderTest):
    """A test whose calls are made in `base`, where the guard stands as it reads them."""

    def drifts(self, tool, given, takes=TAKES):
        """Whether the call of the tool with the input drifts from read_only taking the inputs."""
        event = {"cwd": self.base, "tool_name": tool, "tool_input": given}
        return read_only.drifts(call.read(event), takes)

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


if __name__ == "__main__":
    unittest.main()
