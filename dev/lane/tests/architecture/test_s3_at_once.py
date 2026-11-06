"""S3 of dev/lane/architecture.md, several starts at once, one test for each of its paths:
fan_out.json's routes, the main conversation starting auditor several times at once, its results
taken in the order `more`, `good`, laid by `lay.py write` on a copy of `changelog`; the hooks'
entries as laid called by a double of Claude Code in the test's process; doubles of the main
conversation and the auditors making set calls and giving set results by the result script, each
one its own check takes; and a start made again in place of one with no result, as
docs/routes.md's Runs at once joins it."""

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
        """The main conversation, told to start auditor, starts it twice at once, each start told to
        wait for every start, and ends its turn: what it was told."""
        told = [*self.told]
        for n in (1, 2):
            started = self.claude.start(
                None, auditor(n), f'{{"part": "{["first", "second"][n - 1]}"}}'
            )
            self.assertTrue(started.made, started.said)
            told += started.context
        self.assertTrue(self.claude.end_turn().made)
        return told

    def ends(self, run: testing.Run, on: str) -> list[str]:
        """The start gives the result and ends, and its end reaches the main conversation: what the
        main conversation is told."""
        self.assertTrue(self.result(run, on).made)
        self.assertTrue(self.claude.stop(run).made)
        return self.claude.notify(run)

    def test_every_run_giving_one_result_is_taken_once_both_have_ended(self):
        # Given: the main conversation started auditor twice at once
        started = self.two_runs()
        # When: each gives `good` and ends, each end reaching the main conversation
        after_first = self.ends(auditor(1), "good")
        self.assertTrue(self.claude.end_turn().made)
        after_second = self.ends(auditor(2), "good")
        # Then: the main conversation was told to start auditor, and to wait for every start
        # until both had ended, then told the result of the two and no more starts
        self.assertEqual(started, ["changelog: Start `changelog:auditor`.", WAIT, WAIT])
        self.assertEqual(after_first, [WAIT])
        self.assertEqual(
            after_second, ["changelog: The 2 runs of auditor gave `good`. Start no more subagents."]
        )

    def test_results_that_differ_are_taken_by_precedence(self):
        # Given: the main conversation started auditor twice at once
        self.two_runs()
        # When: the first gives `more` and the second `good`
        self.ends(auditor(1), "more")
        self.claude.end_turn()
        told = self.ends(auditor(2), "good")
        # Then: the main conversation is told `more`, first in precedence, and to start writer
        self.assertEqual(
            told, ["changelog: The 2 runs of auditor gave `more`. Start `changelog:writer`."]
        )

    def test_a_start_before_every_run_has_ended_is_stopped_with_the_wait(self):
        # Given: the main conversation started auditor twice at once, and the first has ended
        self.two_runs()
        self.ends(auditor(1), "more")
        # When: the main conversation starts writer while the second still runs
        told = self.claude.start(None, testing.Run("changelog:writer", "w1"), "Write the entries.")
        # Then: it is denied with follow_routes' sentence and the wait for every run
        self.assertEqual((told.made, told.reason()), (False, f"{FOLLOWED}\n{WAIT}"))

    def test_a_run_ending_with_no_result_is_started_again_once_the_others_have_ended(self):
        # Given: the main conversation started auditor twice at once
        self.two_runs()
        # When: the first ends with no result, kept going once, and ends again; the second gives
        # `good`; and the main conversation starts auditor again, which gives `good`
        kept = self.claude.stop(auditor(1))
        let = self.claude.stop(auditor(1))
        after_first = self.claude.notify(auditor(1))
        self.claude.end_turn()
        after_second = self.ends(auditor(2), "good")
        again = self.claude.start(None, auditor(3), '{"part": "first"}')
        self.claude.end_turn()
        after_third = self.ends(auditor(3), "good")
        # Then: the first was kept going once and let end; the main conversation was told to wait
        # while the second ran, then to start auditor again, and once it gave `good`, no more
        # starts
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
        self.claude.end_turn()
        self.assertTrue(self.result(auditor(2), "more").made)
        self.claude.stop(auditor(2))
        # When: the user lays the routes again with `lay.py write`, auditor no longer
        # fanned out nor its results ordered, before the end reaches the main conversation
        again = self.ux_proposal("fan_out.json")
        del again["routes"]["fan_out"], again["routes"]["precedence"]
        self.lay(again)
        event = {**self.claude.common("UserPromptSubmit", None), "prompt": "x"}
        said = self.claude.send(event)
        # Then: the main conversation is told the result of the starts cannot be told, the maker
        # to order them, and the user is told too
        told = testing.Told(True, said, self.claude.context(said))
        error = (
            "changelog: lane cannot check the routes of write: the runs of auditor at once gave"
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
        # When: the main conversation starts auditor
        told = self.claude.start(None, auditor(1), '{"part": "first"}')
        # Then: it is denied as a call that cannot be checked, naming the laid file and who must
        # fix it, and the operator is told too
        said = (
            "changelog: lane cannot check the routes of write: hooks/lanes.json gives auditor in"
            " `fan_out`, whose results `more` and `good` the routes do not order in"
            " `precedence`, so the result of its runs at once could not be told."
        )
        self.assertEqual((told.made, told.decision()), (False, "deny"))
        self.assertTrue(told.reason().startswith(said), told.reason())
        self.assertIn("must lay its lanes again with `lay.py write`", told.reason())
        self.assertEqual(told.operator(), told.reason())


if __name__ == "__main__":
    unittest.main()
