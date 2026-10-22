"""A tool call read as one action: a Bash call as the commands it runs, in the forms the steps tell
and the AI writes."""

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


class TestOtherTools(unittest.TestCase):
    def test_a_call_of_a_tool_no_lane_watches_is_no_action(self):
        for tool in ("Agent", "Write"):
            with self.subTest(tool=tool):
                # Given: a call of a tool no lane of this version reads, its name sorting before
                # Bash or after
                event = {"cwd": HERE, "tool_name": tool, "tool_input": {"command": "git commit"}}
                # When: it is read
                # Then: it is no action, and runs nothing
                self.assertEqual(call.read(event), call.Call("", []))


if __name__ == "__main__":
    unittest.main()
