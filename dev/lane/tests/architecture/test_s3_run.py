"""S3 of dev/lane/architecture.md, a run, each start told, one test for each of its paths: the
README's walkthrough laid by `lay.py write` and run, and the routes of tests/product-vision/ laid on
a copy of `changelog`, and on a copy of its dependency `checker`; the hooks' entries of both plugins
as laid called by a double of Claude Code in the test's process, which sends the main conversation's
events as a trial on Claude Code 2.1.319 recorded them; doubles of the main conversation, writer,
reviewer and checker's skill making set calls and giving set results by the result scripts, each one
the script's own check takes."""

import os
import unittest

import helpers
from helpers import FOLLOWED, testing


def writer(n: int) -> testing.Run:
    """The nth start of writer."""
    return testing.Run("changelog:writer", f"w{n}")


def reviewer(n: int) -> testing.Run:
    """The nth start of reviewer."""
    return testing.Run("changelog:reviewer", f"r{n}")


class TestWalkthrough(helpers.WalkthroughTest):
    """The README's walkthrough, laid by `lay.py write` as it shows, and run as it shows."""

    def setUp(self) -> None:
        super().setUp()
        self.write("CHANGELOG.md", helpers.CHANGELOG)
        self.git("init", "-q", "-b", "main")
        self.commit()
        self.assertEqual(self.lay_py("write").returncode, 0)
        self.plugin = os.path.join(self.base, "changelog")
        env = {**self.env, "TMPDIR": self.base}
        self.claude = testing.ClaudeCode(self.plugin, self.base, env, check=helpers.handed)

    def gives(self, run: testing.Run, on: str) -> testing.Told:
        """The start's run of its result command on the result, as its step writes it."""
        name = run.kind.split(":")[1]
        command = f"python3 {self.plugin}/hooks/lane/result.py {name} {on}"
        return self.claude.call(run, "Bash", {"command": command, "description": "d"})

    def through(self, run: testing.Run, on: str, command: str = "") -> list[str]:
        """The start of the subagent, its run of the command where one is given, which goes
        through, its result and its end: what the main conversation is told as its end reaches
        it."""
        self.assertTrue(self.claude.start(None, run, "Do your steps.").made)
        self.assertTrue(self.claude.end_turn().made)
        if command:
            ran = self.claude.call(run, "Bash", {"command": command, "description": "d"})
            self.assertTrue(ran.made, ran.said)
        self.assertTrue(self.gives(run, on).made)
        self.assertTrue(self.claude.stop(run).made)
        return self.claude.notify(run)

    def test_the_run_tells_and_stops_as_the_walkthrough_shows(self):
        # Given: the walkthrough's plugin laid, at the root of its repository
        # When: `/changelog:write` is typed
        first = self.claude.typed(helpers.README_TYPED.strip()[1:])
        # And: writer is started, runs git log --oneline, writes CHANGELOG.md, tries git commit,
        # gives `written` and ends
        run = writer(1)
        started = self.claude.start(None, run, "Write the entries.")
        self.claude.end_turn()
        log = self.claude.call(run, "Bash", {"command": "git log --oneline", "description": "d"})
        wrote = self.claude.call(run, "Write", {"file_path": "CHANGELOG.md", "content": "x\n"})
        commit = self.claude.call(run, "Bash", {"command": "git commit -am e", "description": "d"})
        self.assertTrue(self.gives(run, "written").made)
        self.assertTrue(self.claude.stop(run).made)
        written = self.claude.notify(run)
        # And: reviewer, which has no run_only lane, reads the commits with git log --oneline and
        # gives `more`, writer `written` again, and reviewer `good`; then the skill ends its run by
        # its result script with `good`, the result of the route that starts no more
        more = self.through(reviewer(1), "more", "git log --oneline")
        self.through(writer(2), "written")
        good = self.through(reviewer(2), "good")
        command = f"python3 {self.plugin}/hooks/lane/result.py write good"
        ended = self.claude.call(None, "Bash", {"command": command, "description": "d"})
        # Then: the main conversation is told each start as the walkthrough shows, writer is
        # stopped at git commit with its sentence as shown, and its other calls go through
        folder = "<changelog's folder>"
        self.assertEqual(first, [helpers.README_FIRST.strip()])
        self.assertEqual([started.made, log.made, wrote.made], [True, True, True])
        stopped = helpers.README_STOPPED.strip().replace(folder, self.plugin)
        self.assertEqual((commit.made, commit.reason()), (False, stopped))
        self.assertEqual(written, [helpers.README_WRITTEN.strip()])
        self.assertEqual(more, [helpers.README_MORE.strip()])
        self.assertEqual(good, [helpers.README_GOOD.strip()])
        self.assertEqual((ended.made, ended.context), (True, []))
        # And: the run is over, so what is asked next in the conversation is not held
        self.assertTrue(self.claude.end_turn().made)
        self.assertTrue(self.claude.start(None, reviewer(3), "Look again.").made)


class TestBegun(helpers.RunTest):
    """The routes laid, and no run begun yet."""

    def setUp(self) -> None:
        super().setUp()
        self.lay(self.trial_proposal("routes.json"))

    def test_the_skill_called_by_an_ai_begins_the_run_telling_the_first_start(self):
        # Given: the routes laid
        # When: an AI calls the skill write
        called = self.claude.skill("changelog:write")
        # Then: the first start is told as context of the Skill call
        self.assertEqual(called.context, ["changelog: Start `changelog:writer`."])

    def test_outside_a_run_the_main_conversation_is_told_nothing(self):
        # Given: the routes laid, no run begun
        # When: the main conversation starts reviewer, another command is typed, and the turn
        # ends
        started = self.claude.start(None, reviewer(1), "Review the entries.")
        typed = self.claude.typed("changelog:other")
        ended = self.claude.end_turn()
        # Then: each goes on with nothing told
        self.assertEqual((started.made, started.context), (True, []))
        self.assertEqual(typed, [])
        self.assertEqual((ended.made, ended.said), (True, {}))


class TestRun(helpers.RoutesTest):
    def test_the_command_typed_begins_the_run_and_again_tells_nothing(self):
        # Given: `/changelog:write` typed, the first start told
        self.assertEqual(self.told, ["changelog: Start `changelog:writer`."])
        # When: it is typed again while the run is on
        # Then: no other run begins: its expansion tells nothing, and the prompt typed is told the
        # start due, as any prompt within the run is
        self.assertEqual(
            self.claude.typed("changelog:write"), ["changelog: Start `changelog:writer`."]
        )

    def test_written_then_good_ends_the_run(self):
        # Given: the run begun
        # When: writer gives `written`, then reviewer `good`
        after_writer = self.through(writer(1), "written")
        after_reviewer = self.through(reviewer(1), "good")
        # Then: each start is told to wait, and each end the next start, then none
        self.assertEqual(
            after_writer,
            [self.waits("writer"), "changelog: writer gave `written`. Start `changelog:reviewer`."],
        )
        self.assertEqual(
            after_reviewer,
            [self.waits("reviewer"), "changelog: reviewer gave `good`. Start no more subagents."],
        )
        # And: the turn ends
        self.assertTrue(self.claude.end_turn().made)

    def test_more_sends_the_work_back_to_writer_then_good_ends_it(self):
        # Given: the run begun
        # When: writer gives `written`, reviewer `more`, writer `written` again, then reviewer
        # `good`
        told = [
            self.through(writer(1), "written")[-1],
            self.through(reviewer(1), "more")[-1],
            self.through(writer(2), "written")[-1],
            self.through(reviewer(2), "good")[-1],
        ]
        # Then: the work is sent back to writer after `more`, and no more starts after `good`
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
        # Given: the run begun, writer due
        # When: the main conversation starts reviewer
        told = self.claude.start(None, reviewer(1), "Review the entries.")
        # Then: it is denied with follow_routes' sentence and the start due
        reason = f"{FOLLOWED}\nchangelog: Start `changelog:writer`."
        self.assertEqual((told.made, told.reason()), (False, reason))

    def test_a_subagent_that_ended_with_no_result_is_started_again(self):
        # Given: writer started, ending with no result after it was kept going once
        first = writer(1)
        self.claude.start(None, first, "Write the entries.")
        self.claude.end_turn()
        self.claude.stop(first)
        self.claude.stop(first)
        # When: its end reaches the main conversation, which starts writer again, which gives
        # `written`
        told = self.claude.notify(first)
        after = self.through(writer(2), "written")
        # Then: it was told to start writer again, and then reviewer
        again = "changelog: writer ended with no result. Start `changelog:writer` again."
        self.assertEqual(told, [again])
        self.assertEqual(after[-1], "changelog: writer gave `written`. Start `changelog:reviewer`.")

    def test_a_turn_ending_with_a_start_due_is_kept_going_once_then_let_end_the_user_told(self):
        # Given: the run begun, writer due
        # When: the main conversation ends its turn, and, kept going, ends it again
        kept = self.claude.end_turn()
        ended = self.claude.end_turn()
        # Then: it is kept going once with follow_routes' sentence and the start due, then let
        # end, the user told what is left and the step to fix
        reason = f"{FOLLOWED}\nchangelog: Start `changelog:writer`."
        self.assertEqual((kept.made, kept.decision(), kept.reason()), (False, "block", reason))
        left = (
            "changelog: lane let the run of write end with `changelog:writer` still due: the maker"
            " of changelog must fix step 1 of write in skills/write/SKILL.md, which starts it."
        )
        self.assertEqual((ended.made, ended.operator()), (True, left))
        # And: the run is over, so a start goes on
        self.assertTrue(self.claude.start(None, reviewer(1), "Review the entries.").made)

    def test_a_turn_ending_while_a_start_of_the_run_still_runs_ends(self):
        # Given: writer started, still running
        self.claude.start(None, writer(1), "Write the entries.")
        # When: the main conversation ends its turn
        ended = self.claude.end_turn()
        # Then: it ends with nothing told
        self.assertEqual((ended.made, ended.said), (True, {}))


class TestWaits(helpers.RoutesTest):
    """routes.json with reviewer's `asks`, whose route waits for the user, as the sequence's branch
    of a result whose route waits draws."""

    ASKED = (
        "changelog: reviewer gave `asks`. Put its point to the user, and resume"
        " `changelog:reviewer` with their answer by SendMessage."
    )

    def proposed(self) -> dict:
        """The proposal laid: routes.json, with a route from reviewer on `asks` that waits."""
        routed = self.trial_proposal("routes.json")
        routed["routes"]["routes"].append({"from": "reviewer", "on": "asks", "waits": True})
        return routed

    def test_a_result_whose_route_waits_has_the_point_put_and_the_answer_resume_it(self):
        # Given: writer gave `written`
        self.through(writer(1), "written")
        # When: reviewer gives `asks`, the main conversation ends its turn to put the point, and
        # tries a start meanwhile
        told = self.through(reviewer(1), "asks")
        ended = self.claude.end_turn()
        meanwhile = self.claude.start(None, writer(2), "Write again.")
        # Then: it is told to put reviewer's point and resume it with the answer, its turn ends,
        # and the start is denied with that line, as the run goes on
        self.assertEqual(told[-1], self.ASKED)
        self.assertEqual((ended.made, ended.said), (True, {}))
        self.assertEqual((meanwhile.made, meanwhile.reason()), (False, f"{FOLLOWED}\n{self.ASKED}"))
        # And: the user's answer is told the message that resumes reviewer; resumed with it by
        # SendMessage, which Claude Code starts again, reviewer gives `more`, and its end tells
        # the start of writer
        message = f"{helpers.guard.ANSWER}\nIt is 0.2.0."
        resume = "changelog: Resume `changelog:reviewer` by SendMessage with this message, word"
        self.assertEqual(self.claude.prompted("It is 0.2.0."), [f"{resume} for word:\n{message}"])
        sent = self.claude.call(None, "SendMessage", {"to": "r1", "message": message})
        self.claude.started(reviewer(1))
        self.assertTrue(self.result(reviewer(1), "more").made)
        self.claude.stop(reviewer(1))
        after = self.claude.notify(reviewer(1))
        self.assertTrue(sent.made)
        self.assertEqual(after, ["changelog: reviewer gave `more`. Start `changelog:writer`."])
        self.assertTrue(self.claude.start(None, writer(2), "Write again.").made)

    def test_the_skill_typed_again_while_the_user_is_to_answer_begins_another_run(self):
        # Given: writer gave `written`, reviewer `asks`, and the main conversation ended its turn
        # to put the point
        self.through(writer(1), "written")
        self.through(reviewer(1), "asks")
        self.assertTrue(self.claude.end_turn().made)
        # When: the user types `/changelog:write` again in place of an answer
        told = self.claude.typed("changelog:write")
        # Then: the waiting run ends and another begins: its expansion tells the first start,
        # after the line the prompt typed is told, a start of reviewer is stopped with it, and the
        # start of writer goes through
        self.assertEqual(told, [self.ASKED, "changelog: Start `changelog:writer`."])
        meanwhile = self.claude.start(None, reviewer(2), "Review.")
        reason = f"{FOLLOWED}\nchangelog: Start `changelog:writer`."
        self.assertEqual((meanwhile.made, meanwhile.reason()), (False, reason))
        self.assertTrue(self.claude.start(None, writer(2), "Write the entries.").made)


class TestStartText(helpers.RoutesTest):
    """routes.json naming no step of write, whose part holds no numbered list, and the command that
    gives each start its text, as the sequence's branch of a start held to the text that the
    plugin's command gave draws."""

    def proposed(self) -> dict:
        """The proposal laid: routes.json with no step and the command `scripts/start.py`, which
        prints each subagent's values, and write's file holding no numbered list."""
        script = "import json, sys\nprint(json.dumps({'work': sys.argv[1] + '.md'}))\n"
        self.write(os.path.join(self.plugin, "scripts", "start.py"), script)
        self.write(
            os.path.join(self.plugin, "skills", "write", "SKILL.md"),
            "---\nname: write\ndescription: d\n---\n\nHave the entries written and reviewed.\n",
        )
        routed = self.trial_proposal("routes.json")
        del routed["routes"]["step"]
        routed["routes"]["command"] = "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/start.py"
        return routed

    def test_the_run_begins_with_the_routes_sentences_and_each_start_takes_the_text_given(self):
        # Given: the routes laid with no step and the command, and `/changelog:write` typed
        command = f"python3 {self.plugin}/scripts/start.py writer"
        # When: the main conversation starts writer with a text of its own, then runs the command
        # and starts writer with what it printed
        own = self.claude.start(None, writer(1), "Write the entries for 0.2.0.")
        ran = self.claude.call(None, "Bash", {"command": command, "description": "d"})
        given = self.claude.start(None, writer(1), '{"work": "writer.md"}')
        # Then: the run's begin tells the routes' sentence, write's result command and the start
        # with the command to run first; the start with its own text is denied with the text to
        # start it with, the command goes through, and the start with its output goes on
        told = self.told[-1]
        self.assertIn(FOLLOWED, told)
        self.assertIn(
            f"changelog: End by running `python3 {self.plugin}/hooks/lane/result.py", told
        )
        self.assertIn(f"Start `changelog:writer`. Run `{command}` first", told)
        self.assertEqual(own.made, False)
        self.assertIn(f"with what `{command}` printed as its prompt", own.reason())
        self.assertTrue(ran.made)
        self.assertTrue(given.made, given.said)


CHECK = "checker:check"


class TestDependencysSkill(helpers.RoutesTest):
    """Routes from writer to checker's skill check, checker installed in a folder of its own and
    laid by its own proposal, check.json, whose routes start examiner from check and end on its
    `asks` or `done`, the results check ends its run by."""

    def setUp(self) -> None:
        self.installed = ""
        super().setUp()

    def proposed(self) -> dict:
        """The proposal laid: routes.json with writer's `written` leading to check, and check's
        `done` to reviewer, changelog declaring checker, laid first."""
        self.installed = self.checker("check.json")
        routed = self.trial_proposal("routes.json")
        routed["routes"]["routes"][1:2] = [
            {"from": "writer", "on": "written", "to": CHECK},
            {"from": CHECK, "on": "done", "to": "reviewer"},
        ]
        return routed

    def test_the_skill_due_is_one_move_its_result_telling_the_next_start(self):
        # Given: writer gave `written`, so check is due
        told = self.through(writer(1), "written")
        # When: the main conversation calls check, which starts its subagent examiner as checker's
        # routes tell, ends its turn meanwhile, and, once examiner gives `done`, ends check's run
        # by checker's result script with that result, as check's step says
        call = self.claude.skill(CHECK)
        examiner = testing.Run("checker:examiner", "e1")
        meanwhile = self.claude.start(None, examiner, "Check.")
        ended = self.claude.end_turn()
        gave = f"python3 {self.installed}/hooks/lane/result.py examiner done"
        self.assertTrue(
            self.claude.call(examiner, "Bash", {"command": gave, "description": "d"}).made
        )
        self.assertTrue(self.claude.stop(examiner).made)
        over = self.claude.notify(examiner)
        command = f"python3 {self.installed}/hooks/lane/result.py check done"
        done = self.claude.call(None, "Bash", {"command": command, "description": "d"})
        # Then: check was told as due, and checker's guard alone holds its run: it tells the start
        # of examiner and the end, and changelog's guard checks nothing meanwhile; check's result
        # then tells changelog's next start
        self.assertEqual(told[-1], f"changelog: writer gave `written`. Start `{CHECK}`.")
        self.assertEqual((call.made, call.context), (True, ["checker: Start `checker:examiner`."]))
        self.assertEqual((meanwhile.made, ended.made), (True, True))
        self.assertEqual(over, ["checker: examiner gave `done`. Start no more subagents."])
        self.assertEqual(
            (done.made, done.context),
            (True, [f"changelog: {CHECK} gave `done`. Start `changelog:reviewer`."]),
        )
        # And: the start of reviewer goes through
        self.assertTrue(self.claude.start(None, reviewer(1), "Review.").made)

    def test_the_skill_called_while_not_due_is_stopped_with_the_start_due(self):
        # Given: the run begun, writer due
        # When: the main conversation calls check
        called = self.claude.skill(CHECK)
        # Then: it is denied with follow_routes' sentence and the start due
        reason = f"{FOLLOWED}\nchangelog: Start `changelog:writer`."
        self.assertEqual((called.made, called.reason()), (False, reason))


if __name__ == "__main__":
    unittest.main()
