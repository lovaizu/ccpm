"""test_after: a result is given only where each change of the output the lane names was passed: a
test's command, whole, came back without an error after the last Write or Edit of a file under
it."""

import unittest

import helpers
from helpers import test_after

TEST = "python3 -m unittest"
CHANGE = helpers.kept_call("Edit", file_path="src/a.py", old_string="a", new_string="b")
PASSED = helpers.kept_call("Bash", command=TEST, description="d")


class TestMissing(helpers.PluginTest):
    def missing(self, *calls: dict, output: str = "src/") -> str:
        """What test_after taking the output and TEST finds missing after the calls."""
        given = {"output": [output], "test": [TEST]}
        return test_after.missing(given, helpers.did(self.base, self.plugin, list(calls)))

    def test_a_change_passed_after_or_no_change_is_nothing_missing(self):
        for calls in ([CHANGE, PASSED], [PASSED, CHANGE, PASSED], [], [PASSED]):
            with self.subTest(calls=calls):
                # Given: a change and a test passed after, a second change passed again, no
                # change, or a test alone
                # When: the subagent gives its result
                # Then: nothing is missing
                self.assertEqual(self.missing(*calls), "")

    def test_a_change_not_passed_after_is_missing(self):
        other = helpers.kept_call("Bash", command=f"{TEST} -v", description="d")
        for calls in ([CHANGE], [PASSED, CHANGE], [CHANGE, other]):
            with self.subTest(calls=calls):
                # Given: a change with no test after, a test before it alone, or another
                # command after
                # When: the subagent gives its result
                # Then: the change is named as not passed
                self.assertEqual(self.missing(*calls), "`src/` changed with no test passed after")

    def test_a_write_of_another_file_is_no_change(self):
        # Given: a write of a file out of the output
        written = helpers.kept_call("Write", file_path="notes.md", content="x")
        # When: the subagent gives its result
        # Then: nothing is missing
        self.assertEqual(self.missing(written), "")
        # And: a write of the output itself, a file, is one
        self.assertNotEqual(self.missing(written, output="notes.md"), "")


if __name__ == "__main__":
    unittest.main()
