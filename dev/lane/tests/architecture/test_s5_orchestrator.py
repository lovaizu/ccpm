"""S5 of dev/lane/architecture.md, the orchestrator is told each start, one test for each of its
paths: the routes laid by `lay.py write` on a copy of `changelog`, and on a copy of its dependency
`checker` the results of its subagent `examiner`; the hooks' entries of both plugins as laid
called by a double of Claude Code in the test's process, which starts lead from the main
conversation, each subagent lead starts, and lead again once a subagent it started has ended;
doubles of lead, writer, reviewer and examiner making set calls and giving set results by the
result scripts, each one the script's own check takes."""

import glob
import os
import shutil
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

    def test_a_subagent_that_ended_with_no_result_is_started_again(self):
        # Given: lead started writer, which ended with no result after it was kept going once
        first = writer(1)
        self.claude.start(helpers.LEAD_RUN, first, "Write the entries.")
        self.claude.stop(helpers.LEAD_RUN)
        self.claude.stop(first)
        self.claude.stop(first)
        # When: lead starts again, starts writer again, which gives `written`
        told = self.claude.started(helpers.LEAD_RUN)
        after = self.through(writer(2), "written")
        # Then: lead was told to start writer again, and then reviewer
        again = "changelog: writer ended with no result. Start `changelog:writer` again."
        self.assertEqual(told, [again])
        self.assertEqual(after[-1], "changelog: writer gave `written`. Start `changelog:reviewer`.")

    def test_a_run_resumed_after_its_result_gives_a_later_one_and_the_routes_move_on(self):
        # Given: writer gave `written`, then reviewer `good`, so lead was told to start no more
        self.through(writer(1), "written")
        told = self.through(reviewer(1), "good")
        self.assertEqual(told[-1], "changelog: reviewer gave `good`. Start no more subagents.")
        self.claude.stop(helpers.LEAD_RUN)
        # When: the main conversation resumes reviewer by SendMessage, which Claude Code starts
        # again, and it gives `more` and ends
        sent = self.claude.call(None, "SendMessage", {"to": "r1", "message": "Look again."})
        self.claude.started(reviewer(1))
        gave = self.result(reviewer(1), "more")
        self.claude.stop(reviewer(1))
        # Then: lead, started again, is told to start writer, and the start goes through
        after = self.claude.started(helpers.LEAD_RUN)
        self.assertEqual((sent.made, gave.made), (True, True))
        self.assertEqual(after, ["changelog: reviewer gave `more`. Start `changelog:writer`."])
        self.assertTrue(self.claude.start(helpers.LEAD_RUN, writer(2), "Write again.").made)


EXAMINER = testing.Run("checker:examiner", "e1")


class TestDependency(helpers.RoutesTest):
    """Routes from writer to checker's examiner, which gives `asks` to wait for an answer and `done`
    once it can tell, checker installed in a folder of its own and laid by its own proposal."""

    def setUp(self) -> None:
        self.installed = ""
        super().setUp()

    def proposed(self) -> dict:
        """The proposal laid: dependency_routes.json, changelog declaring checker, and checker laid
        first with examiner's results."""
        self.installed = os.path.join(self.base, "cache", "checker", "0.1.0")
        shutil.copytree(os.path.join(helpers.UX, "checker"), self.installed)
        given = self.ux_proposal("examiner.json")
        given["plugin"] = self.installed
        self.lay(given, path=os.path.join(".lane", "20261104-checker", "checker.json"))
        manifest = os.path.join(self.plugin, ".claude-plugin", "plugin.json")
        self.write_json(manifest, {**self.read_json(manifest), "dependencies": ["checker"]})
        self.claude.roots.append(self.installed)
        return self.ux_proposal("dependency_routes.json")

    def examined(self, on: str) -> testing.Told:
        """examiner's run of checker's result command on the result, checker's folder put in, a
        result checker's own result script takes."""
        assert helpers.result.said(["examiner", on], self.installed) == ""
        command = f"python3 {self.installed}/hooks/lane/result.py examiner {on}"
        return self.claude.call(EXAMINER, "Bash", {"command": command, "description": "d"})

    def test_examiner_started_its_result_by_its_own_plugins_script_taken(self):
        # Given: writer gave `written`, so lead is told to start checker's examiner
        told = self.through(writer(1), "written")
        self.assertEqual(told[-1], "changelog: writer gave `written`. Start `checker:examiner`.")
        # When: lead starts examiner, which reads CHANGELOG.md, gives `asks` and ends
        started = self.claude.start(helpers.LEAD_RUN, EXAMINER, "Check CHANGELOG.md.")
        self.claude.stop(helpers.LEAD_RUN)
        read = self.claude.call(EXAMINER, "Read", {"file_path": "CHANGELOG.md"})
        asks = self.examined("asks")
        ended = self.claude.stop(EXAMINER)
        # Then: each goes through, checker's guard and changelog's each keeping the result in a
        # record of its own, and lead, started again, is told to start no more
        for plugin in ("checker", "changelog"):
            (record,) = glob.glob(os.path.join(self.base, "lane", f"*-s1-{plugin}", "e1.jsonl"))
            self.assertIn('"on": "asks"', self.read(record))
        self.assertEqual([t.made for t in (started, read, asks, ended)], [True] * 4)
        after = self.claude.started(helpers.LEAD_RUN)
        self.assertEqual(
            after, ["changelog: checker:examiner gave `asks`. Start no more subagents."]
        )
        # And: once the main conversation resumes examiner with the answer, and it gives `done`,
        # lead is told to start reviewer, as the routes on `done` say
        self.claude.stop(helpers.LEAD_RUN)
        self.claude.call(None, "SendMessage", {"to": "e1", "message": "It is 0.2.0."})
        self.claude.started(EXAMINER)
        self.assertTrue(self.examined("done").made)
        self.claude.stop(EXAMINER)
        after = self.claude.started(helpers.LEAD_RUN)
        self.assertEqual(
            after, ["changelog: checker:examiner gave `done`. Start `changelog:reviewer`."]
        )


if __name__ == "__main__":
    unittest.main()
