"""hands_off: a run of one of the commands the lane takes is a drift, in the forms the steps tell and
the AI writes; every other call is not."""

import unittest

from helpers import NO_PLUGIN, call, hands_off

TAKES = ["git commit", "git push"]


def drifts(command, takes=TAKES):
    event = {"cwd": "/r", "tool_name": "Bash", "tool_input": {"command": command}}
    return hands_off.drifts(call.read(event), takes, NO_PLUGIN)


class TestDrift(unittest.TestCase):
    def test_a_command_taken_run_in_the_forms_the_ai_writes_drifts(self):
        for command in (
            "git commit -m notes",
            "git -C notes commit -m notes",
            "cd notes && git commit -m notes",
            "git add -A; git push origin work",
            "GIT_EDITOR=true git commit",
            "env git commit -m notes",
            "env -u GIT_DIR GIT_EDITOR=true git commit",
            "git --git-dir .git commit -m notes",
        ):
            with self.subTest(command=command):
                # Given: a run of a command the lane takes, in a form the AI writes
                # When: hands_off reads it
                # Then: it is a drift
                self.assertTrue(drifts(command))

    def test_a_command_of_one_word_drifts_whatever_follows_it(self):
        # Given: a lane taking a command of one word
        # When: that command is run with arguments
        # Then: it is a drift
        self.assertTrue(drifts("rm -rf build", ["rm"]))


class TestLetThrough(unittest.TestCase):
    def test_other_commands_are_no_drift(self):
        for command in (
            "git status",
            "git commit-tree HEAD^{tree}",
            "echo git commit",
            "env echo git commit",
            "GIT_EDITOR=true git status",
            "git",
            "",
        ):
            with self.subTest(command=command):
                # Given: a command the lane does not take, one whose words only begin like it,
                # or one naming it as words of another
                # When: hands_off reads it
                # Then: it is no drift
                self.assertFalse(drifts(command))

    def test_a_call_that_runs_nothing_is_no_drift(self):
        # Given: a call of a tool that runs no command
        event = {"cwd": "/r", "tool_name": "Write", "tool_input": {"file_path": "git"}}
        # When: hands_off reads it
        # Then: it is no drift
        self.assertFalse(hands_off.drifts(call.read(event), TAKES, NO_PLUGIN))


if __name__ == "__main__":
    unittest.main()
