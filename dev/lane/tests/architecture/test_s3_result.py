"""S3 of dev/lane/architecture.md, a result given, one test for each of its paths: docs/routes.md's
routes laid by `lay.py write` on a copy of `changelog`, and on a copy of its dependency `checker`
the results of its subagent `examiner`; the hooks' entries of both plugins as laid called by a
double of Claude Code in the test's process; doubles of the main conversation, writer, reviewer and
examiner making set calls and giving set results, each one the result script's own check takes
or, on the path that tries it, one it refuses; and the result scripts run real, as the steps write
them."""

import glob
import os
import unittest

import helpers
from helpers import FOLLOWED, testing


def writer(n: int) -> testing.Run:
    """The nth run of writer."""
    return testing.Run("changelog:writer", f"w{n}")


class TestResult(helpers.RoutesTest):
    def started(self) -> testing.Run:
        """The run's start of writer, the main conversation ending its turn to wait for it."""
        run = writer(1)
        self.claude.start(None, run, "Write the entries.")
        self.claude.end_turn()
        return run

    def test_a_result_a_route_is_on_goes_through_and_is_kept(self):
        # Given: the run's start of writer
        run = self.started()
        # When: writer gives `written`
        gave = self.result(run, "written")
        # Then: the result script runs with nothing said, and the result is kept
        self.assertEqual((gave.made, gave.said), (True, {}))
        self.assertIn({"kind": "result", "on": "written"}, self.kept(run))

    def test_a_result_no_route_is_on_is_stopped_with_the_commands_it_may_run_then_one_it_is_on(
        self,
    ):
        # Given: the run's start of writer
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
        # And: the second goes through and is kept, and its end tells the main conversation to
        # start reviewer
        self.assertEqual((gave.made, gave.said, ended.made), (True, {}, True))
        self.assertEqual(
            [e for e in self.kept(run) if e["kind"] == "result"],
            [{"kind": "result", "on": "written"}],
        )
        told = self.claude.notify(run)
        self.assertEqual(told, ["changelog: writer gave `written`. Start `changelog:reviewer`."])

    def test_an_end_with_a_result_ends_with_nothing_told(self):
        # Given: the run's start of writer, which gave `written`
        run = self.started()
        self.result(run, "written")
        # When: writer is about to end
        ended = self.claude.stop(run)
        # Then: it ends with nothing told, and its end is kept
        self.assertEqual((ended.made, ended.said), (True, {}))
        self.assertEqual(self.kept(run)[-1], {"kind": "end"})

    def test_an_end_with_none_is_kept_going_once_then_let_end(self):
        # Given: the run's start of writer, which gives no result
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
        given = self.trial_proposal("routes.json")
        whole = {"step": 1, "lanes": [{"lane": "read_whole", "takes": ["CHANGELOG.md"]}]}
        given["subagents"][0]["steps"].insert(0, whole)
        return given

    def test_a_result_with_the_work_not_in_form_is_stopped_then_mended_goes_on(self):
        # Given: writer reading CHANGELOG.md to its end, started in the run
        run = writer(1)
        self.claude.start(None, run, "Write the entries.")
        self.claude.end_turn()
        # When: writer gives `written` before it reads CHANGELOG.md, then reads it and gives
        # `written` again, and ends
        stopped = self.result(run, "written")
        self.claude.call(run, "Read", {"file_path": "CHANGELOG.md"})
        gave = self.result(run, "written")
        ended = self.claude.stop(run)
        # Then: the first is denied with step 1, which read_whole holds, and what is missing, the
        # second
        # goes through, and its end tells the main conversation to start reviewer
        said = (
            "changelog: Read `CHANGELOG.md` to learn its last version and its form. Read"
            " `CHANGELOG.md` to its end.\n`CHANGELOG.md` unread from line 1"
        )
        self.assertEqual((stopped.made, stopped.reason()), (False, said))
        self.assertEqual((gave.made, gave.said, ended.made), (True, {}, True))
        told = self.claude.notify(run)
        self.assertEqual(told, ["changelog: writer gave `written`. Start `changelog:reviewer`."])


def reviewer(n: int) -> testing.Run:
    """The nth start of reviewer."""
    return testing.Run("changelog:reviewer", f"r{n}")


class TestResumed(helpers.RoutesTest):
    """A start resumed by the main conversation's SendMessage, as the sequence's last option
    draws."""

    def test_a_message_to_a_start_that_ended_with_no_result_is_stopped(self):
        # Given: writer gave `written`, and reviewer's start ended with no result once kept going
        self.through(writer(1), "written")
        first = reviewer(1)
        self.claude.start(None, first, "Review the entries.")
        self.claude.end_turn()
        self.claude.stop(first)
        self.claude.stop(first)
        told = self.claude.notify(first)
        # When: the main conversation sends it a message
        sent = self.claude.call(None, "SendMessage", {"to": first.agent_id, "message": "Go on."})
        # Then: it was told to start reviewer again, and the message is stopped with that start
        again = "changelog: reviewer ended with no result. Start `changelog:reviewer` again."
        self.assertEqual(told, [again])
        self.assertEqual((sent.made, sent.reason()), (False, f"{FOLLOWED}\n{again}"))

    def test_a_start_resumed_after_its_result_gives_a_later_one_and_the_routes_move_on(self):
        # Given: writer gave `written`, then reviewer `good`, so no more starts were told
        self.through(writer(1), "written")
        told = self.through(reviewer(1), "good")
        self.assertEqual(told[-1], "changelog: reviewer gave `good`. Start no more subagents.")
        # When: the main conversation resumes reviewer by SendMessage, which Claude Code starts
        # again, and it gives `more` and ends
        sent = self.claude.call(None, "SendMessage", {"to": "r1", "message": "Look again."})
        self.claude.started(reviewer(1))
        gave = self.result(reviewer(1), "more")
        self.claude.stop(reviewer(1))
        # Then: its end tells the main conversation to start writer, and the start goes through
        after = self.claude.notify(reviewer(1))
        self.assertEqual((sent.made, gave.made), (True, True))
        self.assertEqual(after, ["changelog: reviewer gave `more`. Start `changelog:writer`."])
        self.assertTrue(self.claude.start(None, writer(2), "Write again.").made)


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
        self.installed = self.checker()
        return self.trial_proposal("dependency_routes.json")

    def examined(self, on: str) -> testing.Told:
        """examiner's run of checker's result command on the result, checker's folder put in, a
        result checker's own result script takes."""
        assert helpers.result.said(["examiner", on], self.installed) == ""
        command = f"python3 {self.installed}/hooks/lane/result.py examiner {on}"
        return self.claude.call(EXAMINER, "Bash", {"command": command, "description": "d"})

    def test_examiners_result_by_its_own_plugins_script_is_taken(self):
        # Given: writer gave `written`, so the main conversation is told to start examiner
        told = self.through(writer(1), "written")
        self.assertEqual(told[-1], "changelog: writer gave `written`. Start `checker:examiner`.")
        # When: examiner is started, reads CHANGELOG.md, gives `asks` and ends
        started = self.claude.start(None, EXAMINER, "Check CHANGELOG.md.")
        self.claude.end_turn()
        read = self.claude.call(EXAMINER, "Read", {"file_path": "CHANGELOG.md"})
        asks = self.examined("asks")
        ended = self.claude.stop(EXAMINER)
        # Then: each goes through, checker's guard and changelog's each keeping the result in a
        # record of its own, and its end tells to put its point to the user, as its route waits
        for plugin in ("checker", "changelog"):
            (record,) = glob.glob(os.path.join(self.base, "lane", f"*-s1-{plugin}", "e1.jsonl"))
            self.assertIn('"on": "asks"', self.read(record))
        self.assertEqual([t.made for t in (started, read, asks, ended)], [True] * 4)
        after = self.claude.notify(EXAMINER)
        asked = (
            "changelog: checker:examiner gave `asks`. Put its point to the user as it wrote it, in"
            " your reply, and resume `checker:examiner` with their answer by SendMessage."
        )
        self.assertEqual(after, [asked])
        # And: once the main conversation resumes examiner with the answer, and it gives `done`,
        # its end tells the start of reviewer, as the routes on `done` say
        self.claude.call(None, "SendMessage", {"to": "e1", "message": "It is 0.2.0."})
        self.claude.started(EXAMINER)
        self.assertTrue(self.examined("done").made)
        self.claude.stop(EXAMINER)
        after = self.claude.notify(EXAMINER)
        self.assertEqual(
            after, ["changelog: checker:examiner gave `done`. Start `changelog:reviewer`."]
        )


if __name__ == "__main__":
    unittest.main()
