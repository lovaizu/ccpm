"""The guard: of a tool call of a subagent with lanes laid, whether it goes through or which
sentences stop it, judged from the call's documented input alone; of a subagent the routes name,
each start of the orchestrator's and each result given, the next start told as it starts and as
each start comes back, and an end kept going while it is due or no result is given; and, where it
cannot judge, the error that says why and who must fix it."""

import os
import unittest

import helpers
from helpers import called, guard

# What a subagent is told, after run_only's sentence, of the commands it may run.
MAY_RUN = "The commands you may run, each word for word: `git log --oneline`."
LAY_AGAIN = (
    "Ask the main conversation for the fix: the maker of changelog must lay its lanes again with"
    " `lay.py write`, so they match its steps. Go on with the rest of your work meanwhile."
)


class GuardTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay()

    def check(self, event: dict, name: str = "writer", wrong: str = "") -> list:
        """What the guard says of the event, of the subagent of the name."""
        return guard.check(self.plugin, "changelog", name, event, wrong)


class TestRun(GuardTest):
    def test_a_command_its_lanes_name_goes_through(self):
        # Given: writer, whose step 2 runs only git log --oneline
        # When: it runs git log --oneline
        # Then: nothing is said, so the call goes on
        self.assertEqual(self.check(self.bash("git log --oneline")), [])

    def test_any_other_command_is_stopped_with_the_sentence_and_the_commands_it_may_run(self):
        for command in ("git commit -m entries", "git log --oneline -3", "ls"):
            with self.subTest(command=command):
                # Given: writer, whose step 2 runs only git log --oneline
                # When: it runs another command
                # Then: it is told the sentence, and on the next line the commands it may run
                self.assertEqual(
                    self.check(self.bash(command)), [guard.Said(f"{helpers.RUN}\n{MAY_RUN}")]
                )

    def test_the_commands_of_every_run_lane_go_through_and_are_told(self):
        # Given: writer running only git log --oneline on step 2 and only git diff on step 3
        self.lay(
            [
                helpers.STEPS[0],
                {"step": 3, "lanes": [{"lane": "run_only", "takes": ["git diff"]}]},
            ],
            helpers.WRITER.replace("--oneline`.\n", f"--oneline`. {helpers.RUN}\n").replace(
                "`CHANGELOG.md`.\n", "`CHANGELOG.md`. Run only `git diff`.\n"
            ),
        )
        # When: it runs git diff, and git commit
        # Then: git diff goes through, and git commit is told both sentences and both commands
        self.assertEqual(self.check(self.bash("git diff")), [])
        commands = "`git log --oneline`, `git diff`"
        told = (
            f"{helpers.RUN}\nRun only `git diff`.\n"
            f"The commands you may run, each word for word: {commands}."
        )
        self.assertEqual(self.check(self.bash("git commit")), [guard.Said(told)])

    def test_a_subagent_with_lanes_and_no_run_lane_runs_no_command(self):
        # Given: writer with write_only alone laid
        self.lay([helpers.STEPS[1]], helpers.LAID.replace(f" {helpers.RUN}", ""))
        # When: it runs a command
        # Then: it is told it may run none
        self.assertEqual(
            self.check(self.bash("git log --oneline")), [guard.Said("You may run no command.")]
        )


class TestWrite(GuardTest):
    def test_an_output_its_lanes_name_is_written(self):
        for tool in ("Write", "Edit"):
            with self.subTest(tool=tool):
                # Given: writer, whose step 3 writes only CHANGELOG.md
                # When: it writes CHANGELOG.md by its whole path
                # Then: the call goes on
                path = os.path.join(self.base, "CHANGELOG.md")
                self.assertEqual(self.check(self.written(path, tool)), [])

    def test_any_other_file_is_stopped_with_the_sentence(self):
        for tool in ("Write", "Edit", "NotebookEdit"):
            with self.subTest(tool=tool):
                # Given: writer, whose step 3 writes only CHANGELOG.md
                # When: it writes another file, a notebook among them
                # Then: it is told the sentence
                self.assertEqual(
                    self.check(self.written("notes.ipynb", tool)), [guard.Said(helpers.WRITE)]
                )

    def test_a_subagent_with_no_write_lane_writes_freely(self):
        # Given: writer with run_only alone laid
        self.lay([helpers.STEPS[0]], helpers.LAID.replace(f" {helpers.WRITE}", ""))
        # When: it writes a file
        # Then: the call goes on
        self.assertEqual(self.check(self.written("any.md")), [])


class TestOther(GuardTest):
    def test_a_tool_no_lane_watches_goes_through(self):
        for tool, given in (
            ("Read", {"file_path": "README.md"}),
            ("Grep", {"pattern": "x"}),
            ("Agent", {"prompt": "p", "subagent_type": "x"}),
        ):
            with self.subTest(tool=tool):
                # Given: writer with its lanes laid
                # When: it uses a tool that neither runs nor writes
                # Then: the call goes on
                self.assertEqual(self.check(self.event(tool, given)), [])

    def test_a_subagent_with_no_lanes_laid_is_not_checked(self):
        # Given: the README's lanes laid in writer alone
        # When: reviewer runs git commit
        # Then: nothing is said, as lane checks only subagents that have rules
        self.assertEqual(self.check(self.bash("git commit"), "reviewer"), [])


class TestCannot(GuardTest):
    def test_lanes_json_that_cannot_be_read_is_an_error_naming_the_fix(self):
        # Given: hooks/lanes.json removed
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        # When: writer runs git log --oneline
        # Then: it is an error, telling what is wrong and who must fix it
        said = "lane cannot check the lanes of writer: hooks/lanes.json is not there. " + LAY_AGAIN
        self.assertEqual(self.check(self.bash("git log --oneline")), [guard.Said(said, True)])

    def test_a_step_no_longer_saying_its_sentence_is_an_error_of_its_lane(self):
        # Given: writer's step 2 no longer saying run_only's sentence
        self.write(self.agent_file, helpers.LAID.replace(f" {helpers.RUN}", ""))
        # When: writer runs git log --oneline
        # Then: it is an error of run_only on step 2, as what it holds no longer reads so
        said = (
            "lane cannot check run_only on step 2 of writer: step 2 no longer says:"
            f" {helpers.RUN} {LAY_AGAIN}"
        )
        self.assertEqual(self.check(self.bash("git log --oneline")), [guard.Said(said, True)])
        # And: a write, which run_only does not judge, goes on
        self.assertEqual(self.check(self.written("CHANGELOG.md")), [])

    def test_an_event_not_as_claude_code_hands_it_is_an_error_for_claude_code(self):
        for event, wrong in (
            (self.bash("ls"), "$.cwd: expected a folder"),
            (self.event("Bash", {"command": 1}), ""),
            (self.event("Write", {"content": "x"}), ""),
        ):
            with self.subTest(event=event, wrong=wrong):
                # Given: an event the hook found wrong, a Bash call of no text, or a Write of
                # no path
                # When: the guard is given it
                said = self.check(event, wrong=wrong)
                # Then: it is an error for Claude Code, telling what is wrong
                self.assertEqual(len(said), 1)
                self.assertTrue(said[0].error)
                self.assertIn(
                    "lane cannot check the lanes of writer: the hook was handed no event as"
                    " Claude Code hands it, ",
                    said[0].text,
                )
                self.assertIn(wrong or "expected a string", said[0].text)
                self.assertIn("`claude update`", said[0].text)


class RoutedTest(GuardTest):
    def setUp(self) -> None:
        super().setUp()
        self.route()
        # The commands writer may give its result by, as it reads them.
        self.writer_gives = f"python3 {self.plugin}/hooks/lane/result.py writer written"

    def told(self, check, event: dict, name: str) -> list:
        """What the guard's check of the event says, of the subagent of the name."""
        return check(self.plugin, "changelog", name, event, "")

    def ran(self, name: str, agent_id: str, on: str) -> None:
        """The subagent of the name and ID started, gave the result and ended, as lead's start of it
        comes back."""
        self.told(guard.started, self.subagent("SubagentStart", name, agent_id), name)
        command = f"python3 {self.plugin}/hooks/lane/result.py {name} {on}"
        self.told(guard.came_back, self.came_back(command, f"changelog:{name}", agent_id), name)
        self.told(guard.stopping, self.subagent("SubagentStop", name, agent_id), name)

    def started_by_lead(self, name: str, back: object) -> list:
        """What lead is told as its start of the subagent of the name comes back with what it gave
        back."""
        return self.told(guard.came_back, self.start(name, "PostToolUse", back), "lead")


class TestFollow(RoutedTest):
    def test_lead_is_told_the_first_start_as_it_starts(self):
        # Given: the routes laid
        # When: lead starts
        # Then: it is told to start writer
        told = self.told(guard.started, self.subagent("SubagentStart", "lead", "lead1"), "lead")
        self.assertEqual(told, [guard.Said("Start `changelog:writer`.")])

    def test_the_start_due_goes_through_and_any_other_call_is_stopped_telling_it(self):
        for event, through in (
            (self.start("writer"), True),
            (self.start("reviewer"), False),
            (
                self.event(
                    "Read", {"file_path": "CHANGELOG.md"}, "changelog:lead", agent_id="lead1"
                ),
                False,
            ),
        ):
            with self.subTest(event=event):
                # Given: no start yet, so writer due
                # When: lead starts writer, starts reviewer, or reads a file
                told = self.told(guard.check, event, "lead")
                # Then: writer's start goes through, and the others are stopped with the
                # sentence and the start due
                due = [guard.Said(helpers.FOLLOW), guard.Said("Start `changelog:writer`.")]
                self.assertEqual(told, [] if through else due)

    def test_each_start_coming_back_tells_the_next_by_the_result_given(self):
        # Given: writer run, giving `written`
        self.ran("writer", "w1", "written")
        # When: lead's start of it comes back
        # Then: lead is told to start reviewer
        told = self.started_by_lead("writer", helpers.back("w1"))
        self.assertEqual(told, [guard.Said("writer gave `written`. Start `changelog:reviewer`.")])
        # And: reviewer run, giving `good`, lead is told to start no more
        self.ran("reviewer", "r1", "good")
        told = self.started_by_lead("reviewer", helpers.back("r1"))
        self.assertEqual(told, [guard.Said("reviewer gave `good`. Start no more subagents.")])
        # And: lead is free after
        self.assertEqual(self.told(guard.check, self.start("reviewer"), "lead"), [])
        later = self.started_by_lead("writer", helpers.back("w2"))
        self.assertEqual(later, [])

    def test_a_start_in_the_background_is_waited_for_and_other_starts_stopped(self):
        # Given: lead's start of writer launched in the background
        told = self.started_by_lead("writer", helpers.back("w1", "async_launched"))
        wait = "Wait for `changelog:writer` to end: you are told the next start once it has."
        # Then: lead is told to wait
        self.assertEqual(told, [guard.Said(wait)])
        # When: lead starts reviewer, reads a file, or is about to end
        # Then: the start is stopped telling it to wait, and the read and the end go on
        stopped = self.told(guard.check, self.start("reviewer"), "lead")
        self.assertEqual(stopped, [guard.Said(helpers.FOLLOW), guard.Said(wait)])
        read = self.event("Read", {"file_path": "CHANGELOG.md"}, "changelog:lead", agent_id="lead1")
        self.assertEqual(self.told(guard.check, read, "lead"), [])
        stop = self.subagent("SubagentStop", "lead", "lead1")
        self.assertEqual(self.told(guard.stopping, stop, "lead"), [])
        # And: once writer has ended with `written`, lead started again is told reviewer
        self.ran("writer", "w1", "written")
        again = self.told(guard.started, self.subagent("SubagentStart", "lead", "lead1"), "lead")
        self.assertEqual(again, [guard.Said("writer gave `written`. Start `changelog:reviewer`.")])

    def test_a_start_that_failed_tells_the_start_still_due(self):
        # Given: lead's start of writer failed
        event = {**self.start("writer", "PostToolUseFailure"), "error": "e", "is_interrupt": False}
        # When: it comes back
        # Then: lead is told writer is still due
        told = self.told(guard.failed, event, "lead")
        self.assertEqual(told, [guard.Said("Start `changelog:writer`.")])

    def test_a_start_not_given_back_as_claude_code_gives_it_is_an_error_and_stays_due(self):
        for back, wrong in (
            ({"status": "teammate_spawned", "agentId": "w1"}, "$.tool_response.status: expected"),
            ({"agentId": "w1"}, 'expected the key "status"'),
            ({"status": "completed"}, 'expected the key "agentId"'),
            ("done", "$.tool_response: expected an object"),
        ):
            with self.subTest(back=back):
                # Given: lead's start of writer coming back with another status, none, or no ID
                # When: it comes back
                told = self.started_by_lead("writer", back)
                # Then: it is an error for Claude Code, and writer is still due
                self.assertTrue(told[0].error)
                self.assertIn(
                    "lane cannot check the lanes of lead: the hook was handed no event as Claude"
                    " Code hands it, ",
                    told[0].text,
                )
                self.assertIn(wrong, told[0].text)
                self.assertEqual(told[1:], [guard.Said("Start `changelog:writer`.")])
                self.assertEqual(called.starts("s1", "lead1", ["writer"], "changelog"), [])

    def test_lead_about_to_end_while_a_start_is_due_is_kept_going(self):
        # Given: writer due
        stop = self.subagent("SubagentStop", "lead", "lead1", active=True)
        # When: lead is about to end, kept going before or not
        # Then: it is told the sentence and the start due
        told = self.told(guard.stopping, stop, "lead")
        self.assertEqual(
            told, [guard.Said(helpers.FOLLOW), guard.Said("Start `changelog:writer`.")]
        )

    def test_lead_ends_once_no_start_is_left(self):
        # Given: writer's `written` and reviewer's `good`
        self.ran("writer", "w1", "written")
        self.started_by_lead("writer", helpers.back("w1"))
        self.ran("reviewer", "r1", "good")
        self.started_by_lead("reviewer", helpers.back("r1"))
        # When: lead is about to end
        # Then: it ends
        stop = self.subagent("SubagentStop", "lead", "lead1")
        self.assertEqual(self.told(guard.stopping, stop, "lead"), [])


class TestResult(RoutedTest):
    def test_the_result_command_goes_through_beside_the_lanes_commands(self):
        # Given: writer, running only git log --oneline and giving `written`
        # When: it runs its result command, as it reads it, or another result
        # Then: its own goes through, and the other is told the commands it may run
        self.assertEqual(self.told(guard.check, self.bash(self.writer_gives), "writer"), [])
        may = (
            "The commands you may run, each word for word: `git log --oneline`,"
            f" `{self.writer_gives}`."
        )
        other = self.bash(self.writer_gives.replace("written", "good"))
        self.assertEqual(
            self.told(guard.check, other, "writer"), [guard.Said(f"{helpers.RUN}\n{may}")]
        )

    def test_a_subagent_with_no_run_lane_runs_its_result_commands_alone(self):
        # Given: reviewer, with no lane but its result commands
        gives = f"python3 {self.plugin}/hooks/lane/result.py reviewer"
        # When: it runs git log --oneline
        told = self.told(
            guard.check, self.bash("git log --oneline", "changelog:reviewer"), "reviewer"
        )
        # Then: it is told the commands it may run
        may = f"The commands you may run, each word for word: `{gives} more`, `{gives} good`."
        self.assertEqual(told, [guard.Said(may)])

    def test_a_subagent_ending_with_no_result_is_kept_going_once_with_its_last_steps_sentence(self):
        # Given: writer started, giving no result
        self.told(guard.started, self.subagent("SubagentStart", "writer", "a1"), "writer")
        # When: it is about to end, and again once kept going
        first = self.told(guard.stopping, self.subagent("SubagentStop", "writer", "a1"), "writer")
        again = self.subagent("SubagentStop", "writer", "a1", active=True)
        # Then: it is told the sentence of its last step, as it reads it, and then ends
        said = f"End by running `{self.writer_gives}`."
        self.assertEqual(first, [guard.Said(said)])
        self.assertEqual(self.told(guard.stopping, again, "writer"), [])
        self.assertTrue(called.ended("s1", "a1"))

    def test_a_result_that_failed_is_not_kept(self):
        # Given: writer's result command failing, its work not in form
        event = {**self.bash(self.writer_gives, held="PostToolUseFailure"), "error": "e"}
        # When: it comes back
        # Then: nothing is told, and no result is kept, so writer is kept going as it ends
        self.assertEqual(self.told(guard.failed, event, "writer"), [])
        self.assertIsNone(called.result("s1", "a1"))

    def test_a_result_given_ends_the_subagent_with_nothing_told(self):
        # Given: writer gave `written`
        self.told(guard.came_back, self.came_back(self.writer_gives), "writer")
        # When: it is about to end
        # Then: it ends
        stop = self.subagent("SubagentStop", "writer", "a1")
        self.assertEqual(self.told(guard.stopping, stop, "writer"), [])
        self.assertEqual(called.result("s1", "a1"), "written")


class TestRoutedCannot(RoutedTest):
    def test_a_step_no_longer_saying_its_routes_sentence_is_an_error(self):
        for file, text, name, event, gone in (
            ("lead.md", helpers.LEAD, "lead", self.start("writer"), "follow_routes on step 1"),
            (
                "writer.md",
                helpers.LAID,
                "writer",
                self.bash("git log --oneline"),
                "result on step 4",
            ),
        ):
            with self.subTest(name=name):
                # Given: lead's step 1 or writer's last step no longer saying its sentence
                self.route()
                self.write(os.path.join(self.plugin, "agents", file), text)
                # When: it makes a call its lanes judge
                told = self.told(guard.check, event, name)
                # Then: it is an error of the sentence's lane
                self.assertEqual(len(told), 1)
                self.assertTrue(told[0].error)
                self.assertIn(f"lane cannot check {gone} of {name}: step", told[0].text)

    def test_kept_calls_that_cannot_be_read_are_an_error(self):
        # Given: lead's calls kept holding a line that is no entry
        called.keep("s1", "lead1", called.START)
        (folder,) = os.listdir(os.path.join(self.base, "lane"))
        with open(os.path.join(self.base, "lane", folder, "lead1.jsonl"), "a") as f:
            f.write("x\n")
        # When: lead starts writer
        told = self.told(guard.check, self.start("writer"), "lead")
        # Then: it is an error, telling it be reported
        self.assertTrue(told[0].error)
        self.assertIn("lane cannot check the lanes of lead: ", told[0].text)
        self.assertIn("https://github.com/lovaizu/ccpm/issues", told[0].text)

    def test_an_event_not_as_claude_code_hands_it_is_an_error_at_every_event(self):
        for check in (guard.came_back, guard.failed, guard.started, guard.stopping):
            with self.subTest(check=check):
                # Given: an event the hook found wrong
                # When: the guard is given it
                said = check(self.plugin, "changelog", "lead", self.start("writer"), "$.cwd: x")
                # Then: it is an error for Claude Code
                self.assertTrue(said[0].error)
                self.assertIn("`claude update`", said[0].text)

    def test_a_subagent_neither_laid_nor_routed_is_not_checked_at_any_event(self):
        for check in (guard.came_back, guard.failed, guard.started, guard.stopping):
            with self.subTest(check=check):
                # Given: the routes laid, naming no planner
                # When: planner's event reaches the guard
                # Then: nothing is said
                self.assertEqual(
                    self.told(check, self.subagent("SubagentStart", "planner", "p1"), "planner"), []
                )


if __name__ == "__main__":
    unittest.main()
