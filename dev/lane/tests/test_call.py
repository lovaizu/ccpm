"""A tool call read as one action: a Bash call as the commands it runs and the files they write, in
the forms the steps tell and the AI writes, and a call of a tool that writes a file as a write of it."""

import unittest

from helpers import call

# The folder each command runs in.
HERE = "/r"


def runs(command):
    """The commands a Bash call of the command runs, as the guard reads it."""
    return call.read({"cwd": HERE, "tool_name": "Bash", "tool_input": {"command": command}})


class TestBash(unittest.TestCase):
    def test_a_bash_call_runs_its_command_with_its_words(self):
        # Given: a Bash call of one command
        # When: it is read
        # Then: it is a run of that command, its words as the shell takes them
        self.assertEqual(
            runs("git commit -m 'a b'"), call.Call("run", [["git", "commit", "-m", "a b"]])
        )

    def test_each_statement_is_a_command_run(self):
        # Given: a Bash call of statements joined by separators
        # When: it is read
        # Then: each statement is a command it runs, in order
        self.assertEqual(
            runs("npm test && npm publish; echo done").what,
            [["npm", "test"], ["npm", "publish"], ["echo", "done"]],
        )

    def test_gits_own_options_before_its_command_are_left_out(self):
        # Given: git with its own options before its command, one taking the next word
        # When: it is read
        # Then: the command run is git's command, as the step names it
        for command in ("git -C notes commit -m m", "git -c a=b --no-pager commit -m m"):
            with self.subTest(command=command):
                self.assertEqual(runs(command).what, [["git", "commit", "-m", "m"]])

    def test_a_cd_before_a_command_is_no_command_run(self):
        # Given: a cd before the command, as the AI writes it to run it in another folder
        # When: it is read
        # Then: the command alone is run
        self.assertEqual(runs("cd notes && git commit").what, [["git", "commit"]])

    def test_a_redirect_and_its_target_are_no_words_of_the_command(self):
        # Given: a command whose output is redirected
        # When: it is read
        # Then: its words leave the redirect and its target out
        self.assertEqual(runs("npm publish > out.txt 2>&1").what, [["npm", "publish"]])

    def test_a_bash_call_without_a_command_runs_nothing(self):
        # Given: a Bash call whose input holds no command
        event = {"cwd": HERE, "tool_name": "Bash", "tool_input": {}}
        # When: it is read
        # Then: it is a run of no command
        self.assertEqual(call.read(event), call.Call("run", []))


class TestWrite(unittest.TestCase):
    def test_a_tool_that_writes_a_file_is_a_write_of_its_path(self):
        for tool, field in (
            ("Write", "file_path"),
            ("Edit", "file_path"),
            ("NotebookEdit", "notebook_path"),
        ):
            with self.subTest(tool=tool):
                # Given: a call of a tool that writes the file its input names
                event = {"cwd": HERE, "tool_name": tool, "tool_input": {field: "/r/CHANGELOG.md"}}
                # When: it is read
                # Then: it is a write of that file, running nothing
                self.assertEqual(call.read(event), call.Call("write", [], ("/r/CHANGELOG.md",)))

    def test_a_path_relative_to_the_folder_is_written_there(self):
        # Given: a Write naming its file from the folder the call is made in
        event = {"cwd": HERE, "tool_name": "Write", "tool_input": {"file_path": "a/../b.md"}}
        # When: it is read
        # Then: the file written is the one the path names from that folder
        self.assertEqual(call.read(event).written, ("/r/b.md",))

    def test_a_write_naming_no_file_writes_none(self):
        # Given: a Write whose input names no file
        event = {"cwd": HERE, "tool_name": "Write", "tool_input": {}}
        # When: it is read
        # Then: it is a write of no file
        self.assertEqual(call.read(event), call.Call("write", [], ()))

    def test_a_bash_call_writes_what_its_commands_write(self):
        # Given: a Bash call whose commands write by a redirect and by cp
        # When: it is read
        # Then: it writes each target, as the shell reads them
        found = runs("echo x > out.txt && cp a.md b.md")
        self.assertEqual(found.written, ("/r/out.txt", "/r/b.md"))


class TestOtherTools(unittest.TestCase):
    def test_a_call_of_a_tool_no_lane_watches_is_no_action(self):
        for tool in ("Agent", "TodoWrite"):
            with self.subTest(tool=tool):
                # Given: a call of a tool no lane of this version reads, its name sorting before
                # Bash or after
                event = {"cwd": HERE, "tool_name": tool, "tool_input": {"command": "git commit"}}
                # When: it is read
                # Then: it is no action, and runs nothing
                self.assertEqual(call.read(event), call.Call("", []))


if __name__ == "__main__":
    unittest.main()
