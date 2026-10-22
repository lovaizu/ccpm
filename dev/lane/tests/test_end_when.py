"""end_when: as the subagent is about to end, an output it has not written in this run, or written
and then removed, is a drift; one there from before it ran is not made."""

import os
import unittest

import helpers
from helpers import bash, call, end_when, failing, testing, writing

TAKES = ["report.md"]


class EndWhenTest(testing.FolderTest):
    def drifts(self, *calls, takes=TAKES):
        """Whether the subagent drifts, about to end having made the calls in the test's folder."""
        return end_when.drifts(call.End(helpers.made(self.base, list(calls)), "", False), takes)

    def there(self, name="report.md"):
        """Puts the file in the test's folder, as the subagent's write leaves it."""
        self.write(os.path.join(self.base, name), "x")


class TestMade(EndWhenTest):
    def test_an_output_written_in_this_run_and_there_is_no_drift(self):
        for made in (writing("report.md"), bash("echo x > report.md"), failing("cp a report.md")):
            with self.subTest(made=made):
                # Given: the output written by the Write tool, a redirect, or a command that wrote
                # it and then failed, and there now
                self.there()
                # When: the subagent is about to end
                # Then: it is no drift
                self.assertFalse(self.drifts(made))

    def test_an_output_never_written_drifts(self):
        for calls in ([], [writing("other.md")], [bash("cat report.md")]):
            with self.subTest(calls=calls):
                # Given: no write of the output in this run, though the file is there from before
                self.there()
                # When: the subagent is about to end
                # Then: it is a drift, as the step's work is to make it
                self.assertTrue(self.drifts(*calls))

    def test_an_output_written_and_then_removed_drifts(self):
        # Given: the output written, then removed, so it is not there
        # When: the subagent is about to end
        # Then: it is a drift
        self.assertTrue(self.drifts(writing("report.md"), bash("rm report.md")))

    def test_a_write_that_failed_does_not_make_it(self):
        # Given: the Write tool giving back an error on the output, the file there from before
        self.there()
        # When: the subagent is about to end
        # Then: it is a drift
        self.assertTrue(self.drifts(writing("report.md", helpers.Failed("stopped"))))


class TestTakes(EndWhenTest):
    def test_any_of_the_outputs_made_is_no_drift(self):
        # Given: a lane taking two outputs, the second written and there
        self.there("b.md")
        # When: the subagent is about to end
        # Then: it is no drift, as the sentence lists them with `or`
        self.assertFalse(self.drifts(writing("b.md"), takes=["a.md", "b.md"]))

    def test_outputs_named_by_no_settled_path_tell_nothing(self):
        # Given: a lane whose output holds a variable, no path being settled
        # When: the subagent is about to end having written nothing
        # Then: it is no drift, as no output can be looked for
        self.assertFalse(self.drifts(takes=["$OUT"]))


if __name__ == "__main__":
    unittest.main()
