"""write_only: a write of anything but the outputs the lane takes is a drift, by a tool that writes a
file or by a command in the forms the steps tell and the AI writes; every other call is not."""

import json
import os
import unittest
from unittest import mock

import helpers
from helpers import NO_PLUGIN, lay, testing
from lanes import write_only
from test_guard import GuardTest

TAKES = ["CHANGELOG.md"]
SENTENCE = "Write only `CHANGELOG.md`."


class WriteOnlyTest(testing.FolderTest):
    """A test whose calls are made in `base`, where the guard stands as it reads them."""

    def drifts(self, tool, given, takes=TAKES):
        """Whether the call of the tool with the input drifts from write_only taking the outputs."""
        event = {"cwd": self.base, "tool_name": tool, "tool_input": given}
        return write_only.drifts(helpers.call_of(event), takes, NO_PLUGIN)

    def bash(self, command, takes=TAKES):
        """Whether a Bash call of the command drifts from write_only taking the outputs."""
        return self.drifts("Bash", {"command": command}, takes)


class TestDrift(WriteOnlyTest):
    def test_a_tool_writing_another_file_drifts(self):
        for tool, given in (
            ("Write", {"file_path": "README.md"}),
            ("Edit", {"file_path": "docs/CHANGELOG.md"}),
            ("NotebookEdit", {"notebook_path": "notes.ipynb"}),
            ("Write", {"file_path": "/tmp/CHANGELOG.md"}),
        ):
            with self.subTest(tool=tool, given=given):
                # Given: write_only taking `CHANGELOG.md`
                # When: a tool writes another file, inside the folder or out of it
                # Then: it is a drift
                self.assertTrue(self.drifts(tool, given))

    def test_a_command_writing_another_file_in_the_folder_drifts(self):
        for command in (
            "echo x > notes.txt",
            "git log >> notes.txt",
            "git log | tee notes.txt",
            "cp CHANGELOG.md CHANGELOG.bak",
            "mv CHANGELOG.md NEWS.md",
            "sed -i s/a/b/ README.md",
            "cd docs && echo x > CHANGELOG.md",
            "echo x > CHANGELOG.md; touch NEWS.md",
        ):
            with self.subTest(command=command):
                # Given: write_only taking `CHANGELOG.md`
                # When: a command writes another file in the folder the call is made in, in a form
                # the AI writes
                # Then: it is a drift
                self.assertTrue(self.bash(command))


class TestLetThrough(WriteOnlyTest):
    def test_a_tool_writing_the_output_is_no_drift(self):
        for tool, path in (
            ("Write", "CHANGELOG.md"),
            ("Write", "./CHANGELOG.md"),
            ("Write", "docs/../CHANGELOG.md"),
            ("Edit", os.path.join(self.base, "CHANGELOG.md")),
        ):
            with self.subTest(tool=tool, path=path):
                # Given: write_only taking `CHANGELOG.md`
                # When: a tool writes it, named from the folder however the path is written, or
                # whole
                # Then: it is no drift
                self.assertFalse(self.drifts(tool, {"file_path": path}))

    def test_a_command_writing_the_output_is_no_drift(self):
        for command in (
            "echo x >> CHANGELOG.md",
            "sed -i s/a/b/ CHANGELOG.md",
            "cd docs && cat a.md > ../CHANGELOG.md",
        ):
            with self.subTest(command=command):
                # Given: write_only taking `CHANGELOG.md`
                # When: a command writes it, from where the call is made or from a folder below
                # Then: it is no drift
                self.assertFalse(self.bash(command))

    def test_an_output_taken_as_a_whole_path_is_the_one_written_from_the_folder(self):
        # Given: write_only taking the output as a whole path
        takes = [os.path.join(self.base, "CHANGELOG.md")]
        # When: Write names it from the folder
        # Then: it is no drift
        self.assertFalse(self.drifts("Write", {"file_path": "CHANGELOG.md"}, takes))

    def test_an_output_taken_from_the_home_folder_is_the_one_there(self):
        # Given: write_only taking an output named from the home folder, `base` here
        with mock.patch.dict(os.environ, {"HOME": self.base}):
            # When: a tool writes that file
            # Then: it is no drift
            self.assertFalse(
                self.drifts("Write", {"file_path": "CHANGELOG.md"}, ["~/CHANGELOG.md"])
            )

    def test_any_of_the_outputs_taken_is_no_drift(self):
        # Given: write_only taking two outputs
        takes = ["CHANGELOG.md", "NEWS.md"]
        # When: a command writes the second
        # Then: it is no drift
        self.assertFalse(self.bash("echo x > NEWS.md", takes))

    def test_a_command_writing_out_of_the_folder_is_no_drift(self):
        for command in ("git status > /dev/null 2>&1", "git log > /tmp/log.txt"):
            with self.subTest(command=command):
                # Given: write_only taking `CHANGELOG.md`
                # When: a command writes out of the folder the call is made in, as one throwing its
                # output away, or keeping it in a folder of its own to run what the work gives
                # Then: it is no drift
                self.assertFalse(self.bash(command))

    def test_a_call_writing_nothing_is_no_drift(self):
        for tool, given in (
            ("Bash", {"command": "git status"}),
            ("Bash", {"command": "cat README.md"}),
            ("Read", {"file_path": "README.md"}),
        ):
            with self.subTest(tool=tool, given=given):
                # Given: write_only taking `CHANGELOG.md`
                # When: a call writes nothing
                # Then: it is no drift
                self.assertFalse(self.drifts(tool, given))


class TestLaid(GuardTest):
    """write_only laid on step 3 of changelog-writer, run by the guard as Claude Code runs it."""

    def setUp(self) -> None:
        super().setUp()
        laid = helpers.STEPS.replace("`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {SENTENCE}\n")
        self.write(self.agent_file, laid)

    def written(self, path):
        """The guard on changelog-writer writing the path with Write."""
        event = self.event("", tool="Write")
        event["tool_input"] = {"file_path": path}
        return self.guard(json.dumps(event), (helpers.AGENT, "3:write_only:CHANGELOG.md"))

    def test_a_write_of_another_file_is_stopped_with_the_sentence(self):
        # Given: write_only on step 3 of changelog-writer
        # When: changelog-writer writes README.md
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin
        self.assertEqual(self.written("README.md"), (2, f"notes: {SENTENCE}\n"))

    def test_a_write_of_the_output_is_let_through(self):
        # Given: write_only on step 3 of changelog-writer
        # When: changelog-writer writes CHANGELOG.md
        # Then: the call goes on, nothing said
        self.assertEqual(self.written("CHANGELOG.md"), (0, ""))


class TestHook(unittest.TestCase):
    def test_the_hook_watches_each_tool_that_writes_once_beside_another_lanes(self):
        # Given: write_only and hands_off laid on one step, both watching Bash
        lanes = [
            {"lane": "hands_off", "takes": ["git commit"]},
            {"lane": "write_only", "takes": TAKES},
        ]
        # When: the layer makes the subagent's hook
        entry = lay.entry(
            "notes", {"name": "writer", "steps": [{"step": 3, "lanes": lanes}]}, "PreToolUse"
        )
        # Then: its matcher names each tool the two watch, once
        assert entry is not None, "no entry was made"
        self.assertEqual(entry["matcher"], "Bash|Write|Edit|NotebookEdit")


if __name__ == "__main__":
    unittest.main()
