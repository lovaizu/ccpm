"""S4 of dev/lane/architecture.md, a subagent gives its result, one test for each of its paths:
docs/routes.md's routes laid by `lay.py write` on a copy of `changelog`; the hooks' entries as
laid called by a double of Claude Code in the test's process; doubles of lead, writer and
reviewer making set calls and giving set results, each one the result script's own check takes or,
on the path that tries it, one it refuses; and the result script run real, as the step writes it."""

import unittest

import helpers
from helpers import testing


def writer(n: int) -> testing.Run:
    """The nth run of writer."""
    return testing.Run("changelog:writer", f"w{n}")


class TestResult(helpers.RoutesTest):
    def started(self) -> testing.Run:
        """lead's run of writer, started, lead ended to wait for it."""
        run = writer(1)
        self.claude.start(helpers.LEAD_RUN, run, "Write the entries.")
        self.claude.stop(helpers.LEAD_RUN)
        return run

    def test_a_result_a_route_is_on_goes_through_and_is_kept(self):
        # Given: lead's run of writer
        run = self.started()
        # When: writer gives `written`
        gave = self.result(run, "written")
        # Then: the result script runs with nothing said, and the result is kept
        self.assertEqual((gave.made, gave.said), (True, {}))
        self.assertIn({"kind": "result", "on": "written"}, self.kept(run))

    def test_a_result_no_route_is_on_is_stopped_with_the_commands_it_may_run_then_one_it_is_on(
        self,
    ):
        # Given: lead's run of writer
        run = self.started()
        # When: writer gives `good`, which no route from it is on, then `written`, and ends
        stopped = self.result(run, "good", refused=True)
        gave = self.result(run, "written")
        ended = self.claude.stop(run)
        # Then: the first is denied before the result script runs, with run_only's sentence and
        # the commands it may run, its result command among them
        said = (
            "changelog: Run only `git log --oneline`.\n"
            "The commands you may run, each word for word: `git log --oneline`,"
            f" `{self.gives(run, 'written')}`."
        )
        self.assertEqual((stopped.made, stopped.reason()), (False, said))
        # And: the second goes through and is kept, and lead, started again, is told reviewer
        self.assertEqual((gave.made, gave.said, ended.made), (True, {}, True))
        self.assertEqual(
            [e for e in self.kept(run) if e["kind"] == "result"],
            [{"kind": "result", "on": "written"}],
        )
        told = self.claude.started(helpers.LEAD_RUN)
        self.assertEqual(told, ["changelog: writer gave `written`. Start `changelog:reviewer`."])

    def test_an_end_with_a_result_ends_with_nothing_told(self):
        # Given: lead's run of writer, which gave `written`
        run = self.started()
        self.result(run, "written")
        # When: writer is about to end
        ended = self.claude.stop(run)
        # Then: it ends with nothing told, and its end is kept
        self.assertEqual((ended.made, ended.said), (True, {}))
        self.assertEqual(self.kept(run)[-1], {"kind": "end"})

    def test_an_end_with_none_is_kept_going_once_then_let_end(self):
        # Given: lead's run of writer, which gives no result
        run = self.started()
        # When: writer is about to end, and again once kept going
        kept = self.claude.stop(run)
        ended = self.claude.stop(run)
        # Then: it is kept going once with its last step's sentence, then let end with no result
        said = f"changelog: End by running `{self.gives(run, 'written')}`.{helpers.NOT_WORK}"
        self.assertEqual((kept.made, kept.decision(), kept.reason()), (False, "block", said))
        self.assertTrue(ended.made)
        self.assertNotIn("result", [e["kind"] for e in self.kept(run)])


class TestWorkNotInForm(helpers.RoutesTest):
    def proposed(self) -> dict:
        """routes.json with writer also reading CHANGELOG.md to its end on its step 1, a lane
        checked as it gives its result."""
        given = self.ux_proposal("routes.json")
        whole = {"step": 1, "lanes": [{"lane": "read_whole", "takes": ["CHANGELOG.md"]}]}
        given["subagents"][0]["steps"].insert(0, whole)
        return given

    def test_a_result_with_the_work_not_in_form_is_stopped_then_mended_goes_on(self):
        # Given: writer reading CHANGELOG.md to its end, started by lead, which waits
        run = writer(1)
        self.claude.start(helpers.LEAD_RUN, run, "Write the entries.")
        self.claude.stop(helpers.LEAD_RUN)
        # When: writer gives `written` before it reads CHANGELOG.md, then reads it and gives
        # `written` again, and ends
        stopped = self.result(run, "written")
        self.claude.call(run, "Read", {"file_path": "CHANGELOG.md"})
        gave = self.result(run, "written")
        ended = self.claude.stop(run)
        # Then: the first is denied with read_whole's sentence and what is missing, the second
        # goes through, and lead, started again, is told to start reviewer
        said = "changelog: Read `CHANGELOG.md` to its end.\n`CHANGELOG.md` unread from line 1"
        self.assertEqual((stopped.made, stopped.reason()), (False, said))
        self.assertEqual((gave.made, gave.said, ended.made), (True, {}, True))
        told = self.claude.started(helpers.LEAD_RUN)
        self.assertEqual(told, ["changelog: writer gave `written`. Start `changelog:reviewer`."])


if __name__ == "__main__":
    unittest.main()
