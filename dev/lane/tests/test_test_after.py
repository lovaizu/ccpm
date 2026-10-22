"""test_after: as the subagent is about to end, its last change to the output with no passing run of
the test after it is a drift; a run passes where its Bash call gave back no error."""

import os
import unittest

import helpers
from helpers import bash, call, failing, test_after, testing, writing

# The output and the test the lane takes, as a step names them.
TAKES = ["app.py", "python3 -m unittest"]
# The output changed by the Write tool, and the test run with no error, words after the test's own.
CHANGE, PASS = writing("app.py"), bash("python3 -m unittest discover -s tests")


class TestAfter(testing.FolderTest):
    def drifts(self, *calls, takes=TAKES):
        """Whether the subagent drifts, about to end having made the calls in the test's folder."""
        return test_after.drifts(call.End(helpers.made(self.base, list(calls)), "", False), takes)


class TestChanged(TestAfter):
    def test_a_change_with_a_passing_run_after_it_is_no_drift(self):
        # Given: the output changed, then the test run with no error
        # When: the subagent is about to end
        # Then: it is no drift
        self.assertFalse(self.drifts(CHANGE, PASS))

    def test_a_change_with_no_run_after_it_drifts(self):
        # Given: the output changed and the test never run
        # When: the subagent is about to end
        # Then: it is a drift
        self.assertTrue(self.drifts(CHANGE))

    def test_a_change_after_the_last_passing_run_drifts(self):
        # Given: the test passed, then the output changed again
        # When: the subagent is about to end
        # Then: it is a drift, the last change not yet passed
        self.assertTrue(self.drifts(CHANGE, PASS, CHANGE))

    def test_a_failing_run_after_the_change_does_not_pass_it(self):
        # Given: the output changed, then the test run giving back an error
        # When: the subagent is about to end
        # Then: it is a drift
        self.assertTrue(self.drifts(CHANGE, failing("python3 -m unittest")))

    def test_a_run_of_another_command_does_not_pass_it(self):
        for command in ("python3 -m pytest", "python3 -m", "ls", "app.py", "ruff check"):
            with self.subTest(command=command):
                # Given: the output changed, then another command run with no error, sorting
                # before the test or after it, the test's first words alone, or the output itself
                # When: the subagent is about to end
                # Then: it is a drift
                self.assertTrue(self.drifts(CHANGE, bash(command)))

    def test_a_run_of_the_test_after_a_cd_passes_it(self):
        # Given: the output changed, then the test run after a cd with no error
        # When: the subagent is about to end
        # Then: it is no drift
        self.assertFalse(self.drifts(CHANGE, bash(f"cd {self.base} && python3 -m unittest")))

    def test_a_run_whose_exit_is_the_tests_passes_it(self):
        for command in ("python3 -m unittest && echo ok", "make && python3 -m unittest -v"):
            with self.subTest(command=command):
                # Given: the output changed, then a call with no error whose commands after the
                # test, if any, are joined to it by &&, so a failing test would end it in error
                # When: the subagent is about to end
                # Then: it is no drift
                self.assertFalse(self.drifts(CHANGE, bash(command)))

    def test_a_run_whose_exit_may_not_be_the_tests_does_not_pass_it(self):
        for command in (
            "python3 -m unittest; echo exit=$?",
            "python3 -m unittest 2>&1 | tail -5",
            "python3 -m unittest || true",
            "python3 -m unittest && echo ok; echo done",
            "python3 -m unittest\necho done",
        ):
            with self.subTest(command=command):
                # Given: the output changed, then a call with no error whose exit is a later
                # command's whatever the test gave, as the AI writes to see the test's exit
                # When: the subagent is about to end
                # Then: it is a drift, as no pass is shown
                self.assertTrue(self.drifts(CHANGE, bash(command)))

    def test_any_of_the_tests_taken_passes_it(self):
        # Given: a lane taking two tests, and the output changed, then the second run
        takes = ["app.py", "ruff check", "python3 -m unittest"]
        # When: the subagent is about to end
        # Then: it is no drift
        self.assertFalse(self.drifts(CHANGE, PASS, takes=takes))

    def test_a_command_changing_the_output_and_running_the_test_passes_it(self):
        # Given: one Bash call changing the output in place, then running the test, with no error
        # When: the subagent is about to end
        # Then: it is no drift
        self.assertFalse(self.drifts(bash("sed -i s/a/b/ app.py && python3 -m unittest")))

    def test_a_command_changing_the_output_and_failing_is_a_change(self):
        # Given: one Bash call changing the output in place, then running the test, which fails
        # When: the subagent is about to end
        # Then: it is a drift, as the change was made before the command failed
        self.assertTrue(self.drifts(failing("sed -i s/a/b/ app.py && python3 -m unittest")))


class TestUnchanged(TestAfter):
    def test_no_change_to_the_output_is_no_drift(self):
        for calls in ([], [writing("other.py")], [bash("cat app.py")]):
            with self.subTest(calls=calls):
                # Given: calls changing no output: none, another file written, the output read
                # When: the subagent is about to end
                # Then: it is no drift, the step's test being for a change to the output
                self.assertFalse(self.drifts(*calls))

    def test_a_write_that_failed_is_no_change(self):
        # Given: the Write tool giving back an error on the output, as when a hook stopped it
        # When: the subagent is about to end
        # Then: it is no drift, nothing having been written
        self.assertFalse(self.drifts(writing("app.py", helpers.Failed("stopped"))))

    def test_the_output_is_named_from_the_folder_the_subagent_ends_in(self):
        # Given: the output written by its whole path
        # When: the subagent is about to end, with no run after it
        # Then: it is a drift, the path being the output's
        self.assertTrue(self.drifts(writing(os.path.join(self.base, "app.py"))))

    def test_an_output_named_by_no_settled_path_is_never_changed(self):
        # Given: a lane whose output holds a variable, and a write of a file of that name
        # When: the subagent is about to end
        # Then: it is no drift, as no path is settled to have been changed
        self.assertFalse(self.drifts(writing("$OUT"), takes=["$OUT", "make test"]))


if __name__ == "__main__":
    unittest.main()
