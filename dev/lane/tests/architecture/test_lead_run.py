"""An orchestrator on a run, lead's of the UX's O2, each path of its sequence in
dev/lane/architecture.md from start to end: docs/routes.md's routes laid by `lay.py write` on a
copy of `changelog`, the hooks' commands as laid run in sh by a double of Claude Code, which starts
lead from the main conversation, each subagent lead starts, and lead again once a subagent it
started has ended; doubles of lead, writer and reviewer make set calls and give set results by the
result script, run as the step writes it."""

import unittest

import helpers
from helpers import FOLLOWED, testing


def writer(n: int) -> testing.Run:
    """The nth run of writer."""
    return testing.Run("changelog:writer", f"w{n}")


def reviewer(n: int) -> testing.Run:
    """The nth run of reviewer."""
    return testing.Run("changelog:reviewer", f"r{n}")


class TestLeadRun(helpers.RoutesTest):
    def test_written_then_good_ends_the_run(self):
        # Given: the routes laid, and lead started, told to start writer
        self.assertEqual(self.told.context, ["changelog: Start `changelog:writer`."])
        # When: writer gives `written`, then reviewer `good`
        after_writer = self.through(writer(1), "written")
        after_reviewer = self.through(reviewer(1), "good")
        # Then: lead is told to wait for each, and after each the next start, then none
        self.assertEqual(
            after_writer,
            [self.waits("writer"), "changelog: writer gave `written`. Start `changelog:reviewer`."],
        )
        self.assertEqual(
            after_reviewer,
            [self.waits("reviewer"), "changelog: reviewer gave `good`. Start no more subagents."],
        )
        # And: lead ends
        self.assertTrue(self.claude.stop(helpers.LEAD_RUN).made)

    def test_more_sends_the_work_back_to_writer_then_good_ends_it(self):
        # Given: the routes laid, and lead started
        # When: writer gives `written`, reviewer `more`, writer `written` again, then reviewer
        # `good`
        told = [
            self.through(writer(1), "written")[-1],
            self.through(reviewer(1), "more")[-1],
            self.through(writer(2), "written")[-1],
            self.through(reviewer(2), "good")[-1],
        ]
        # Then: lead is sent back to writer after `more`, and told no more after `good`
        self.assertEqual(
            told,
            [
                "changelog: writer gave `written`. Start `changelog:reviewer`.",
                "changelog: reviewer gave `more`. Start `changelog:writer`.",
                "changelog: writer gave `written`. Start `changelog:reviewer`.",
                "changelog: reviewer gave `good`. Start no more subagents.",
            ],
        )

    def test_a_start_no_route_names_is_stopped_with_the_start_due(self):
        # Given: the routes laid, and lead started, told to start writer
        # When: lead starts reviewer
        told = self.claude.start(helpers.LEAD_RUN, reviewer(1), "Review the entries.")
        # Then: it is denied with follow_routes' sentence and the start due
        reason = f"{FOLLOWED}\nchangelog: Start `changelog:writer`."
        self.assertEqual((told.made, told.reason()), (False, reason))

    def test_a_subagent_ending_with_no_result_is_kept_going_once(self):
        # Given: the routes laid, and lead started writer, which runs
        run = writer(1)
        self.claude.start(helpers.LEAD_RUN, run, "Write the entries.")
        self.claude.stop(helpers.LEAD_RUN)
        # When: writer ends with no result, then gives `written` and ends
        kept = self.claude.stop(run)
        gave = self.result(run, "written")
        ended = self.claude.stop(run)
        # Then: it is kept going once with its last step's sentence, then let end, and lead,
        # started again, is told to start reviewer
        said = f"changelog: End by running `{self.gives(run, 'written')}`."
        self.assertEqual((kept.made, kept.decision(), kept.reason()), (False, "block", said))
        self.assertEqual((gave.made, ended.made), (True, True))
        told = self.claude.started(helpers.LEAD_RUN)
        self.assertEqual(told, ["changelog: writer gave `written`. Start `changelog:reviewer`."])

    def test_a_result_no_route_is_on_is_stopped_with_the_commands_it_may_run_then_one_it_is_on(
        self,
    ):
        # Given: the routes laid, and lead started writer, which runs
        run = writer(1)
        self.claude.start(helpers.LEAD_RUN, run, "Write the entries.")
        self.claude.stop(helpers.LEAD_RUN)
        # When: writer gives `good`, which no route from it is on, then `written`, and ends
        stopped = self.result(run, "good")
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

    def test_a_run_with_no_result_resumed_by_sendmessage_is_stopped(self):
        # Given: writer gave `written`, and lead started reviewer, which ended with no result after
        # it was kept going once
        self.through(writer(1), "written")
        first = reviewer(1)
        self.claude.start(helpers.LEAD_RUN, first, "Review the entries.")
        self.claude.stop(helpers.LEAD_RUN)
        self.claude.stop(first)
        self.claude.stop(first)
        told = self.claude.started(helpers.LEAD_RUN)
        message = {"to": first.agent_id, "message": "Go on."}
        # When: lead sends a message to that run, then starts reviewer again, and sends a message
        # to that run again
        before = self.claude.call(helpers.LEAD_RUN, "SendMessage", message)
        again = self.claude.start(helpers.LEAD_RUN, reviewer(2), "Review the entries.")
        after = self.claude.call(helpers.LEAD_RUN, "SendMessage", message)
        # Then: lead is told to start reviewer again, and each message is denied with
        # follow_routes' sentence and the start due: the start again, then the wait for it
        start_again = "changelog: reviewer ended with no result. Start `changelog:reviewer` again."
        self.assertEqual(told, [start_again])
        self.assertEqual((before.made, before.reason()), (False, f"{FOLLOWED}\n{start_again}"))
        self.assertTrue(again.made, again.said)
        self.assertEqual(
            (after.made, after.reason()), (False, f"{FOLLOWED}\n{self.waits('reviewer')}")
        )
        # And: once the run started again gives `good`, lead is told no more starts
        self.claude.stop(helpers.LEAD_RUN)
        self.assertTrue(self.result(reviewer(2), "good").made)
        self.claude.stop(reviewer(2))
        told = self.claude.started(helpers.LEAD_RUN)
        self.assertEqual(told, ["changelog: reviewer gave `good`. Start no more subagents."])

    def test_lead_kept_going_once_with_a_start_due_is_then_let_end_the_operator_told(self):
        # Given: the routes laid, and lead started, told to start writer
        # When: lead ends with writer's start due, and, kept going, ends again
        kept = self.claude.stop(helpers.LEAD_RUN)
        ended = self.claude.stop(helpers.LEAD_RUN)
        # Then: it is kept going once with follow_routes' sentence and the start due, then let
        # end, the operator told what is left and the step to fix
        reason = f"{FOLLOWED}\nchangelog: Start `changelog:writer`."
        self.assertEqual((kept.made, kept.decision(), kept.reason()), (False, "block", reason))
        left = (
            "changelog: lane let lead end with `changelog:writer` still due: the maker of"
            " changelog must fix step 1 of lead in agents/lead.md, which starts it."
        )
        self.assertEqual((ended.made, ended.operator()), (True, left))


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
