"""Runs at once of a subagent the routes name in `fan_out`, each path of its sequence in
dev/lane/architecture.md from start to end: fan_out.json's routes, lead starting runs of auditor at
once, its results taken in the order `more`, `good`, laid by `lay.py write` on a copy of
`changelog`, the hooks' commands as laid run in sh by a double of Claude Code; doubles of lead and
the auditors make set calls and give set results by the result script, run as the step writes
it; and a run started again in place of one with no result, as docs/routes.md's Runs at once
joins it."""

import os
import unittest

import helpers
from helpers import FOLLOWED, testing


def auditor(n: int) -> testing.Run:
    """The nth run of auditor."""
    return testing.Run("changelog:auditor", f"a{n}")


WAIT = (
    "changelog: Wait for every run of `changelog:auditor` to end: you are told the next start once"
    " each has."
)


class TestRunsAtOnce(helpers.RoutesTest):
    def proposed(self) -> dict:
        """The proposal laid: fan_out.json."""
        return self.ux_proposal("fan_out.json")

    def two_runs(self) -> list[str]:
        """lead, told to start auditor, starts two runs of it at once, each told to wait for every
        run, and ends: what it was told."""
        told = [*self.told.context]
        for n in (1, 2):
            started = self.claude.start(
                helpers.LEAD_RUN, auditor(n), f'{{"part": "{["first", "second"][n - 1]}"}}'
            )
            self.assertTrue(started.made, started.said)
            told += started.context
        self.assertTrue(self.claude.stop(helpers.LEAD_RUN).made)
        return told

    def ends(self, run: testing.Run, on: str) -> list[str]:
        """The run gives the result and ends, and lead is started again: what lead is told."""
        self.assertTrue(self.result(run, on).made)
        self.assertTrue(self.claude.stop(run).made)
        return self.claude.started(helpers.LEAD_RUN)

    def test_every_run_giving_one_result_is_taken_once_both_have_ended(self):
        # Given: lead started two runs of auditor at once
        started = self.two_runs()
        # When: each gives `good` and ends, lead started again after each
        after_first = self.ends(auditor(1), "good")
        self.assertTrue(self.claude.stop(helpers.LEAD_RUN).made)
        after_second = self.ends(auditor(2), "good")
        # Then: lead was told to start auditor, and to wait for every run until both had ended,
        # then told the result of the two and no more starts
        self.assertEqual(started, ["changelog: Start `changelog:auditor`.", WAIT, WAIT])
        self.assertEqual(after_first, [WAIT])
        self.assertEqual(
            after_second, ["changelog: The 2 runs of auditor gave `good`. Start no more subagents."]
        )

    def test_results_that_differ_are_taken_by_precedence(self):
        # Given: lead started two runs of auditor at once
        self.two_runs()
        # When: the first gives `more` and the second `good`
        self.ends(auditor(1), "more")
        self.claude.stop(helpers.LEAD_RUN)
        told = self.ends(auditor(2), "good")
        # Then: lead is told `more`, first in precedence, and to start writer
        self.assertEqual(
            told, ["changelog: The 2 runs of auditor gave `more`. Start `changelog:writer`."]
        )

    def test_a_start_before_every_run_has_ended_is_stopped_with_the_wait(self):
        # Given: lead started two runs of auditor at once, and the first has ended
        self.two_runs()
        self.ends(auditor(1), "more")
        # When: lead starts writer while the second still runs
        told = self.claude.start(
            helpers.LEAD_RUN, testing.Run("changelog:writer", "w1"), "Write the entries."
        )
        # Then: it is denied with follow_routes' sentence and the wait for every run
        self.assertEqual((told.made, told.reason()), (False, f"{FOLLOWED}\n{WAIT}"))

    def test_a_run_ending_with_no_result_is_started_again_once_the_others_have_ended(self):
        # Given: lead started two runs of auditor at once
        self.two_runs()
        # When: the first ends with no result, kept going once, and ends again; the second gives
        # `good`; and lead starts auditor again, which gives `good`
        kept = self.claude.stop(auditor(1))
        let = self.claude.stop(auditor(1))
        after_first = self.claude.started(helpers.LEAD_RUN)
        self.claude.stop(helpers.LEAD_RUN)
        after_second = self.ends(auditor(2), "good")
        again = self.claude.start(helpers.LEAD_RUN, auditor(3), '{"part": "first"}')
        self.claude.stop(helpers.LEAD_RUN)
        after_third = self.ends(auditor(3), "good")
        # Then: the first was kept going once and let end; lead was told to wait while the second
        # ran, then to start auditor again, and once it gave `good`, no more starts
        self.assertEqual((kept.made, kept.decision(), let.made), (False, "block", True))
        self.assertEqual(after_first, [WAIT])
        self.assertEqual(
            after_second,
            ["changelog: auditor ended with no result. Start `changelog:auditor` again."],
        )
        self.assertTrue(again.made, again.said)
        self.assertEqual(
            after_third, ["changelog: The 2 runs of auditor gave `good`. Start no more subagents."]
        )

    def test_results_the_routes_laid_again_do_not_order_are_an_error_the_operator_told(self):
        # Given: two runs of auditor at once, the first giving `good` and the second `more`
        self.two_runs()
        self.ends(auditor(1), "good")
        self.claude.stop(helpers.LEAD_RUN)
        self.assertTrue(self.result(auditor(2), "more").made)
        self.claude.stop(auditor(2))
        # When: the developer AI lays the routes again with `lay.py write`, auditor no longer
        # fanned out nor its results ordered, before lead is started again
        again = self.ux_proposal("fan_out.json")
        del again["routes"]["fan_out"], again["routes"]["precedence"]
        self.lay(again)
        said = self.claude.send(self.claude.common("SubagentStart", helpers.LEAD_RUN))
        # Then: lead is told the results of the runs cannot be told, the maker to order them,
        # and the operator is told too
        told = testing.Told(True, said, self.claude.context(said))
        error = (
            "changelog: lane cannot check the lanes of lead: the runs of auditor at once gave"
            " `good` and `more`, and the routes order not each of them in `precedence`."
        )
        self.assertEqual(len(told.context), 1)
        self.assertTrue(told.context[0].startswith(error), told.context[0])
        self.assertIn("must order the results of auditor in the `precedence`", told.context[0])
        self.assertEqual(told.operator(), told.context[0])

    def test_laid_routes_lay_py_print_would_refuse_are_an_error_the_operator_told(self):
        # Given: the laid routes edited by hand, auditor fanned out with no order of its results
        laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
        del laid["routes"]["precedence"]
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        # When: lead starts auditor
        told = self.claude.start(helpers.LEAD_RUN, auditor(1), '{"part": "first"}')
        # Then: it is denied as a call that cannot be checked, naming the laid file and who must
        # fix it, and the operator is told too
        said = (
            "changelog: lane cannot check the lanes of lead: hooks/lanes.json gives auditor in"
            " `fan_out`, whose results `more` and `good` the routes do not order in"
            " `precedence`, so the result of its runs at once could not be told."
        )
        self.assertEqual((told.made, told.decision()), (False, "deny"))
        self.assertTrue(told.reason().startswith(said), told.reason())
        self.assertIn("must lay its lanes again with `lay.py write`", told.reason())
        self.assertEqual(told.operator(), told.reason())


class TestRunInPlace(helpers.RoutesTest):
    """The routes of docs/routes.md, reviewer not fanned out, its run started again joined in place
    of one with no result."""

    def test_a_run_with_no_result_resumed_by_another_gives_a_result_out_of_the_count(self):
        # Given: writer gave `written`, reviewer ended with no result after it was kept going
        # once, and lead started reviewer again, which runs
        self.through(testing.Run("changelog:writer", "w1"), "written")
        first, second = (
            testing.Run("changelog:reviewer", "r1"),
            testing.Run("changelog:reviewer", "r2"),
        )
        self.claude.start(helpers.LEAD_RUN, first, "Review the entries.")
        self.claude.stop(helpers.LEAD_RUN)
        self.claude.stop(first)
        self.claude.stop(first)
        self.claude.started(helpers.LEAD_RUN)
        self.claude.start(helpers.LEAD_RUN, second, "Review the entries.")
        self.claude.stop(helpers.LEAD_RUN)
        # When: the main conversation resumes the first run by SendMessage, which gives `more` and
        # ends, then the run started again gives `good` and ends
        sent = self.claude.call(None, "SendMessage", {"to": first.agent_id, "message": "Go on."})
        self.claude.started(first)
        gave = self.result(first, "more")
        self.claude.stop(first)
        after_first = self.claude.started(helpers.LEAD_RUN)
        self.claude.stop(helpers.LEAD_RUN)
        self.assertTrue(self.result(second, "good").made)
        self.claude.stop(second)
        after_second = self.claude.started(helpers.LEAD_RUN)
        # Then: the message and the first run's `more` go through and the result is kept
        self.assertEqual((sent.made, gave.made), (True, True))
        self.assertIn({"kind": "result", "on": "more"}, self.kept(first))
        # And: lead waits for the run started again, and is told the route on its `good`, the
        # first run out of the count
        self.assertEqual(after_first, [self.waits("reviewer")])
        self.assertEqual(
            after_second, ["changelog: reviewer gave `good`. Start no more subagents."]
        )


if __name__ == "__main__":
    unittest.main()
