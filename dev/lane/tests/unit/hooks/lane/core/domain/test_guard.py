"""The guard: of a tool call of a subagent with lanes laid, whether it goes through or which
sentences stop it, judged from the call's documented input alone; of a subagent the routes name,
each start of the orchestrator's and each result given, the next start told as it starts and as
each start comes back, and an end kept going while it is due or no result is given; and, where it
cannot judge, the error that says why and who must fix it."""

import json
import os
import subprocess
import unittest
from unittest import mock

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


class TestDependency(GuardTest):
    def test_a_command_of_a_dependencys_skill_goes_through_by_its_folder(self):
        # Given: writer running only checker's command, checker declared and installed
        manifest = {"name": "changelog", "version": "0.1.0", "dependencies": ["checker"]}
        self.write_json(self.manifest(), manifest)
        self.write_json(
            os.path.join("checker", ".claude-plugin", "plugin.json"), {"name": "checker"}
        )
        take = "python3 ${dependency:checker}/scripts/check.py CHANGELOG.md"
        self.lay(
            [{"step": 2, "lanes": [{"lane": "run_only", "takes": [take]}]}],
            helpers.WRITER.replace("--oneline`.\n", f"--oneline`. Run only `{take}`.\n"),
        )
        folder = os.path.join(self.base, "checker")
        # When: it runs the command by checker's folder, and by another
        # Then: the first goes through, and the second is told the sentence, the command it may
        # run and what the folder in it stands for
        self.assertEqual(
            self.check(self.bash(f"python3 {folder}/scripts/check.py CHANGELOG.md")), []
        )
        told = self.check(self.bash(f"python3 {self.base}/scripts/check.py CHANGELOG.md"))
        self.assertEqual(
            told,
            [
                guard.Said(
                    f"Run only `{take}`.\nThe commands you may run, each word for word: `{take}`."
                    "\nEach `${dependency:<name>}` is the folder the plugin of the name is"
                    " installed in, as its skill gives the command."
                )
            ],
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

    def test_a_tools_field_not_as_claude_code_gives_it_is_named_by_its_place(self):
        for event, point in (
            (self.event("Write", {"file_path": 1, "content": "x"}), "$.tool_input.file_path:"),
            (self.event("Bash", {"description": "d"}), "$.tool_input.command:"),
        ):
            with self.subTest(event=event):
                # Given: a Write of a path not a text, or a Bash call of no command
                # When: the guard is given it
                said = self.check(event)
                # Then: the error names the field's place in the event
                self.assertIn(
                    f"the hook was handed no event as Claude Code hands it, {point} expected a"
                    " string",
                    said[0].text,
                )


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


class TestRoutedDependency(RoutedTest):
    """A subagent of a dependency the routes name, checker's examiner: changelog's guard checks
    none of its calls, which its own plugin's guard holds, and keeps its results and its end as it
    does those of changelog's own subagents."""

    def setUp(self) -> None:
        super().setUp()
        self.depend()
        self.folder = os.path.join(self.base, "checker")

    def examined(self, on: str) -> str:
        """examiner's result command on the result, checker's folder put in."""
        return f"python3 {self.folder}/hooks/lane/result.py examiner {on}"

    def test_lead_is_told_to_start_examiner_after_written_and_its_start_goes_through(self):
        # Given: writer, started by lead, gave `written`
        self.started_by_lead("writer", helpers.back("w1", "async_launched"))
        self.ran("writer", "w1", "written")
        # When: lead starts again, and starts examiner
        told = self.told(guard.started, self.subagent("SubagentStart", "lead", "lead1"), "lead")
        start = self.told(guard.check, self.start("checker:examiner"), "lead")
        # Then: it is told to start examiner by its type, and the start goes through
        self.assertEqual(told[-1], guard.Said("writer gave `written`. Start `checker:examiner`."))
        self.assertEqual(start, [])

    def test_examiners_calls_are_left_to_its_own_plugins_guard(self):
        # Given: examiner, whose calls changelog lays no lane on
        event = self.event("Bash", {"command": "rm -r ."}, "checker:examiner", agent_id="e1")
        # When: it runs a command
        # Then: changelog's guard tells it nothing
        self.assertEqual(self.told(guard.check, event, "checker:examiner"), [])

    def test_examiners_result_by_its_plugins_script_is_kept_and_leads_lead_on(self):
        # Given: lead started writer, which gave `written`, then examiner
        self.started_by_lead("writer", helpers.back("w1", "async_launched"))
        self.ran("writer", "w1", "written")
        self.started_by_lead("checker:examiner", helpers.back("e1", "async_launched"))
        name = "checker:examiner"
        # When: examiner starts, gives `asks` by checker's script, and ends
        self.told(guard.started, self.subagent("SubagentStart", name, "e1"), name)
        back = self.came_back(self.examined("asks"), name, "e1")
        self.assertEqual(self.told(guard.came_back, back, name), [])
        self.assertEqual(
            self.told(guard.stopping, self.subagent("SubagentStop", name, "e1"), name), []
        )
        # Then: its result is kept in changelog's record, and lead is told to start no more
        self.assertEqual(called.result(helpers.KEPT, "e1"), "asks")
        told = self.told(guard.started, self.subagent("SubagentStart", "lead", "lead1"), "lead")
        self.assertEqual(
            told[-1], guard.Said("checker:examiner gave `asks`. Start no more subagents.")
        )

    def test_a_command_no_route_from_examiner_is_on_keeps_no_result(self):
        for command in (
            self.examined("good"),
            f"python3 {self.base}/hooks/lane/result.py examiner asks",
        ):
            with self.subTest(command=command):
                # Given: examiner started
                name = "checker:examiner"
                self.told(guard.started, self.subagent("SubagentStart", name, "e1"), name)
                # When: it gives a result no route is on, or by a folder that is not checker's
                self.told(guard.came_back, self.came_back(command, name, "e1"), name)
                # Then: no result is kept
                self.assertIsNone(called.result(helpers.KEPT, "e1"))

    def test_examiner_ending_with_no_result_is_kept_going_once_with_its_commands(self):
        # Given: examiner started, giving no result
        name = "checker:examiner"
        self.told(guard.started, self.subagent("SubagentStart", name, "e1"), name)
        # When: it is about to end, and again after it was kept going
        first = self.told(guard.stopping, self.subagent("SubagentStop", name, "e1"), name)
        again = self.told(guard.stopping, self.subagent("SubagentStop", name, "e1", True), name)
        # Then: it is kept going once, told the commands and what checker's folder stands for,
        # and then let end, its end kept
        said = (
            f"End by running `{helpers.EXAMINED} asks` or `{helpers.EXAMINED} done`.\n"
            "Each `${dependency:<name>}` is the folder the plugin of the name is installed in, as"
            " its skill gives the command."
        )
        self.assertEqual(first, [guard.Said(said)])
        self.assertEqual(again, [])
        self.assertTrue(called.ended(helpers.KEPT, "e1"))

    def test_lead_let_end_with_examiner_due_again_tells_whose_fix_it_is(self):
        # Given: examiner started by lead, ending with no result, kept going once
        name = "checker:examiner"
        self.told(guard.started, self.subagent("SubagentStart", name, "e1"), name)
        for active in (False, True):
            self.told(guard.stopping, self.subagent("SubagentStop", name, "e1", active), name)
        self.started_by_lead(name, helpers.back("e1"))
        # When: lead, kept going once with examiner due again, is about to end again
        stop = self.subagent("SubagentStop", "lead", "lead1", active=True)
        # Then: the operator is told the maker of checker or of changelog must fix it
        said = (
            "lane let lead end with `checker:examiner` still due, as checker:examiner ended with"
            " no result the routes take: the maker of checker must have examiner give `asks` or"
            " `done`, or the maker of changelog must route the result it gives."
        )
        self.assertEqual(self.told(guard.stopping, stop, "lead"), [guard.Said(said, note=True)])

    def test_another_plugins_subagent_is_left_alone_where_lanes_json_cannot_be_read(self):
        # Given: hooks/lanes.json removed
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        # When: examiner is about to end
        event = self.subagent("SubagentStop", "checker:examiner", "e1")
        # Then: changelog's guard tells it nothing, as whether the routes name it cannot be read,
        # and changelog's own subagents are told the error
        self.assertEqual(self.told(guard.stopping, event, "checker:examiner"), [])

    def test_a_dependencys_subagent_the_routes_do_not_name_is_left_alone(self):
        # Given: checker's linter, which the routes do not name
        event = self.subagent("SubagentStop", "checker:linter", "x1")
        # When: it is about to end
        # Then: changelog's guard tells it nothing and keeps nothing
        self.assertEqual(self.told(guard.stopping, event, "checker:linter"), [])
        self.assertEqual(called.kept(helpers.KEPT, "x1"), [])


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
                self.assertEqual(called.starts(helpers.KEPT, "lead1", ["writer"], "changelog"), [])

    def test_lead_about_to_end_while_a_start_is_due_is_kept_going_once(self):
        # Given: writer due, never started
        # When: lead is about to end
        # Then: it is told the sentence and the start due
        told = self.told(guard.stopping, self.subagent("SubagentStop", "lead", "lead1"), "lead")
        self.assertEqual(
            told, [guard.Said(helpers.FOLLOW), guard.Said("Start `changelog:writer`.")]
        )
        # And: about to end again, kept going once, it ends, the operator told what is left and
        # who must fix it, lead's step that starts it
        again = self.subagent("SubagentStop", "lead", "lead1", active=True)
        said = (
            "lane let lead end with `changelog:writer` still due: the maker of changelog must fix"
            " step 1 of lead in agents/lead.md, which starts it."
        )
        self.assertEqual(self.told(guard.stopping, again, "lead"), [guard.Said(said, note=True)])
        self.assertTrue(called.ended(helpers.KEPT, "lead1"))

    def test_a_subagent_ended_with_no_result_is_started_again_once_then_lead_may_end(self):
        # Given: writer started by lead, ending with no result, kept going once
        self.told(guard.started, self.subagent("SubagentStart", "writer", "w1"), "writer")
        for active in (False, True):
            stop = self.subagent("SubagentStop", "writer", "w1", active=active)
            self.told(guard.stopping, stop, "writer")
        # When: lead's start of it comes back
        told = self.started_by_lead("writer", helpers.back("w1"))
        # Then: lead is told to start it again
        again = "writer ended with no result. Start `changelog:writer` again."
        self.assertEqual(told, [guard.Said(again)])
        # And: about to end, lead is kept going once with it
        stop = self.subagent("SubagentStop", "lead", "lead1")
        self.assertEqual(
            self.told(guard.stopping, stop, "lead"), [guard.Said(helpers.FOLLOW), guard.Said(again)]
        )
        # And: about to end again, it ends, the operator told that writer's step giving its
        # result must be fixed
        stop = self.subagent("SubagentStop", "lead", "lead1", active=True)
        said = (
            "lane let lead end with `changelog:writer` still due, as writer ended with no result:"
            " the maker of changelog must fix step 4 of writer in agents/writer.md, which gives its"
            " result."
        )
        self.assertEqual(self.told(guard.stopping, stop, "lead"), [guard.Said(said, note=True)])

    def ended_with_none(self) -> None:
        """writer started by lead, ending with no result after it was kept going once, and lead's
        start of it come back."""
        self.told(guard.started, self.subagent("SubagentStart", "writer", "w1"), "writer")
        for active in (False, True):
            stop = self.subagent("SubagentStop", "writer", "w1", active=active)
            self.told(guard.stopping, stop, "writer")
        self.started_by_lead("writer", helpers.back("w1"))

    def sent(self, to: str) -> dict:
        """lead's SendMessage call to the run of the ID."""
        given = {"to": to, "message": "Go on."}
        return self.event("SendMessage", given, "changelog:lead", agent_id="lead1")

    def test_a_message_to_a_run_ended_with_no_result_before_its_start_again_is_stopped(self):
        # Given: writer ended with no result after it was kept going once
        self.ended_with_none()
        # When: lead sends a message to that run before it starts writer again
        told = self.told(guard.check, self.sent("w1"), "lead")
        # Then: it is denied with follow_routes' sentence and the start due
        again = "writer ended with no result. Start `changelog:writer` again."
        self.assertEqual(told, [guard.Said(helpers.FOLLOW), guard.Said(again)])

    def test_a_message_to_a_run_ended_with_no_result_after_its_start_again_is_stopped(self):
        # Given: writer ended with no result after it was kept going once, and lead started it
        # again, which runs
        self.ended_with_none()
        self.started_by_lead("writer", helpers.back("w2", "async_launched"))
        # When: lead sends a message to the run that ended with no result
        told = self.told(guard.check, self.sent("w1"), "lead")
        # Then: it is denied with follow_routes' sentence and the start due, the wait for the run
        # started again
        waits = "Wait for `changelog:writer` to end: you are told the next start once it has."
        self.assertEqual(told, [guard.Said(helpers.FOLLOW), guard.Said(waits)])

    def test_a_message_to_a_run_that_gave_a_result_goes_through(self):
        # Given: writer gave `written`, and lead started reviewer, which runs
        self.ran("writer", "w1", "written")
        self.started_by_lead("writer", helpers.back("w1"))
        self.started_by_lead("reviewer", helpers.back("r1", "async_launched"))
        # When: lead sends a message to writer's run
        # Then: it goes through, telling nothing
        self.assertEqual(self.told(guard.check, self.sent("w1"), "lead"), [])

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

    def test_a_subagent_the_routes_start_is_told_no_start_as_it_starts(self):
        # Given: the routes laid, lead their orchestrator
        # When: writer starts
        # Then: it is told nothing, as only lead is told the starts
        told = self.told(guard.started, self.subagent("SubagentStart", "writer", "w1"), "writer")
        self.assertEqual(told, [])

    def test_leads_other_calls_come_back_kept_telling_nothing(self):
        # Given: writer due
        read = self.event("Read", {"file_path": "CHANGELOG.md"}, "changelog:lead", agent_id="lead1")
        back = {**read, "hook_event_name": "PostToolUse", "tool_response": {"file": "x"}}
        failed = {**read, "hook_event_name": "PostToolUseFailure", "error": "e"}
        # When: lead's read comes back, and fails
        # Then: nothing is told, and the read is kept as a call of lead's
        self.assertEqual(self.told(guard.came_back, back, "lead"), [])
        self.assertEqual(self.told(guard.failed, failed, "lead"), [])
        self.assertEqual([c["tool"] for c in called.calls(helpers.KEPT, "lead1")], ["Read"])

    def test_a_start_failing_once_no_start_is_left_tells_nothing(self):
        # Given: writer's `written` and reviewer's `good`
        self.ran("writer", "w1", "written")
        self.started_by_lead("writer", helpers.back("w1"))
        self.ran("reviewer", "r1", "good")
        self.started_by_lead("reviewer", helpers.back("r1"))
        # When: lead's start of writer fails
        event = {**self.start("writer", "PostToolUseFailure"), "error": "e", "is_interrupt": False}
        # Then: nothing is told, as lead is free
        self.assertEqual(self.told(guard.failed, event, "lead"), [])


class TestFanOut(RoutedTest):
    """reviewer fanned out, its results taken in the order `more`, `good`."""

    WAIT = (
        "Wait for every run of `changelog:reviewer` to end: you are told the next start once each"
        " has."
    )

    def setUp(self) -> None:
        super().setUp()
        self.fan_out(["more", "good"])
        # Given: writer run, giving `written`, so reviewer is due
        self.ran("writer", "w1", "written")
        self.started_by_lead("writer", helpers.back("w1"))

    def fan_out(self, precedence: object) -> None:
        """Lays the routes with reviewer fanned out, its results in the order given, or none."""
        routed = {**helpers.ROUTES, "fan_out": ["reviewer"]}
        routed.update({"precedence": precedence} if precedence else {})
        laid = {**helpers.RULES, "routes": routed}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def launched(self, *agents: str) -> list:
        """What lead is told as each of its starts of reviewer, of the IDs, goes through and comes
        back launched in the background, the last of them."""
        told: list = []
        for agent in agents:
            self.assertEqual(self.told(guard.check, self.start("reviewer"), "lead"), [])
            told = self.started_by_lead("reviewer", helpers.back(agent, "async_launched"))
        return told

    def lead_started(self) -> list:
        """What lead is told as Claude Code starts it again."""
        return self.told(guard.started, self.subagent("SubagentStart", "lead", "lead1"), "lead")

    def test_lead_may_start_several_runs_and_is_told_the_next_once_every_one_has_ended(self):
        # When: lead starts reviewer twice
        # Then: both go through, lead told to wait for every run as each comes back
        self.assertEqual(self.launched("r1", "r2"), [guard.Said(self.WAIT)])
        # And: the second is kept joined to the first
        joined = [
            c.get("joined") for c in called.calls(helpers.KEPT, "lead1") if c["tool"] == "Agent"
        ]
        self.assertEqual(joined, [None, None, "more"])
        # And: writer's start is stopped while either runs, and once the first gives `more`
        stopped = [guard.Said(helpers.FOLLOW), guard.Said(self.WAIT)]
        self.assertEqual(self.told(guard.check, self.start("writer"), "lead"), stopped)
        self.ran("reviewer", "r1", "more")
        self.assertEqual(self.lead_started(), [guard.Said(self.WAIT)])
        self.assertEqual(self.told(guard.check, self.start("writer"), "lead"), stopped)
        # And: once the second ends with `good`, lead is told writer, by the order of the results
        self.ran("reviewer", "r2", "good")
        told = [guard.Said("The 2 runs of reviewer gave `more`. Start `changelog:writer`.")]
        self.assertEqual(self.lead_started(), told)
        self.assertEqual(self.told(guard.check, self.start("writer"), "lead"), [])

    def test_a_start_of_another_subagent_than_the_one_due_is_kept_joined_to_none(self):
        # Given: reviewer due
        # When: lead's start of writer comes back, though the hook stops such a start
        self.started_by_lead("writer", helpers.back("w2", "async_launched"))
        # Then: it is kept joined to no start before it
        last = [c for c in called.calls(helpers.KEPT, "lead1") if c["tool"] == "Agent"][-1]
        self.assertNotIn("joined", last)

    def test_a_run_ending_with_no_result_has_reviewer_started_again_into_the_runs(self):
        # Given: two runs of reviewer, the first giving `good`, the second ending with no result
        # after it was kept going once
        self.launched("r1", "r2")
        self.ran("reviewer", "r1", "good")
        self.told(guard.started, self.subagent("SubagentStart", "reviewer", "r2"), "reviewer")
        for active in (False, True):
            stop = self.subagent("SubagentStop", "reviewer", "r2", active=active)
            self.told(guard.stopping, stop, "reviewer")
        # When: Claude Code starts lead again
        # Then: it is told to start reviewer again
        again = "reviewer ended with no result. Start `changelog:reviewer` again."
        self.assertEqual(self.lead_started(), [guard.Said(again)])
        # And: the run started again gives `more`, which is taken with the first run's `good`
        self.launched("r3")
        self.ran("reviewer", "r3", "more")
        told = [guard.Said("The 2 runs of reviewer gave `more`. Start `changelog:writer`.")]
        self.assertEqual(self.lead_started(), told)

    def test_runs_giving_differing_results_the_routes_laid_again_do_not_order_are_an_error(self):
        # Given: two runs of reviewer at once, giving `more` and `good`
        self.launched("r1", "r2")
        self.ran("reviewer", "r1", "more")
        self.ran("reviewer", "r2", "good")
        # When: the routes are laid again with reviewer no longer fanned out nor its results
        # ordered, before lead is told the next start
        laid = {**helpers.RULES, "routes": helpers.ROUTES}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        # Then: lead is told the error, with who must fix it
        told = self.lead_started()
        self.assertEqual(
            told,
            [
                guard.Said(
                    "lane cannot check the lanes of lead: the runs of reviewer at once gave `more`"
                    " and `good`, and the routes order not each of them in `precedence`. Ask the"
                    " main conversation for the fix: the maker of changelog must order the results"
                    " of reviewer in the `precedence` of its routes, and lay them again with"
                    " `lay.py write`. Go on with the rest of your work meanwhile.",
                    True,
                )
            ],
        )


class TestJoinedStart(unittest.TestCase):
    def test_a_start_joins_the_runs_only_of_the_subagent_due_or_waited_for(self):
        more = helpers.routes.Next("wait", "reviewer", None, more=True)
        again = helpers.routes.Next("start", "reviewer", None, True)
        due = helpers.routes.Next("start", "reviewer", ("writer", "written"))
        # reviewer read from JSON, not a text the code writes.
        same = json.loads('"reviewer"')
        for before, name, found in (
            (more, same, "more"),
            (again, same, "again"),
            (due, same, ""),
            (more, "author", ""),
            (more, "writer", ""),
            (again, "author", ""),
            (again, "writer", ""),
        ):
            with self.subTest(before=before, name=name):
                # Given: runs of reviewer that more may join, reviewer due again, or due anew
                # When: lead's start of reviewer, or of a subagent named before or after it,
                # comes back
                # Then: only reviewer's joins, as a further run or one started again
                self.assertEqual(guard.joined(before, name), found)


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
        self.assertTrue(called.ended(helpers.KEPT, "a1"))

    def test_a_result_that_failed_is_not_kept(self):
        # Given: writer's result command failing, its work not in form
        event = {**self.bash(self.writer_gives, held="PostToolUseFailure"), "error": "e"}
        # When: it comes back
        # Then: nothing is told, and no result is kept, so writer is kept going as it ends
        self.assertEqual(self.told(guard.failed, event, "writer"), [])
        self.assertIsNone(called.result(helpers.KEPT, "a1"))

    def test_a_result_given_ends_the_subagent_with_nothing_told(self):
        # Given: writer gave `written`
        self.told(guard.came_back, self.came_back(self.writer_gives), "writer")
        # When: it is about to end
        # Then: it ends
        stop = self.subagent("SubagentStop", "writer", "a1")
        self.assertEqual(self.told(guard.stopping, stop, "writer"), [])
        self.assertEqual(called.result(helpers.KEPT, "a1"), "written")

    def test_a_call_other_than_its_result_command_keeps_no_result(self):
        # Given: writer, giving `written`
        # When: its git log --oneline comes back
        self.told(guard.came_back, self.came_back("git log --oneline"), "writer")
        # Then: no result is kept, so writer is kept going as it ends
        self.assertIsNone(called.result(helpers.KEPT, "a1"))

    def test_a_result_is_kept_beside_lanes_checked_at_the_end(self):
        # Given: writer, giving `written`, ending once report.md is made
        self.write("report.md", "x")
        laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
        laid["subagents"][0]["steps"].append(
            {"step": 3, "lanes": [{"lane": "end_when", "takes": ["report.md"]}]}
        )
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        self.write(
            self.agent_file,
            helpers.WRITER_LAID.replace(
                "`CHANGELOG.md`.\n", "`CHANGELOG.md`. End only once `report.md` is made.\n"
            ),
        )
        # When: its result command comes back
        self.told(guard.came_back, self.came_back(self.writer_gives), "writer")
        # Then: its result is kept
        self.assertEqual(called.result(helpers.KEPT, "a1"), "written")

    def test_a_call_of_another_tool_holding_the_result_command_keeps_no_result(self):
        for tool in ("Agent", "Read"):
            with self.subTest(tool=tool):
                # Given: writer, giving `written`
                # When: a call of another tool comes back, its input holding the result command
                event = self.event(tool, {"command": self.writer_gives}, held="PostToolUse")
                self.told(guard.came_back, {**event, "tool_response": {}}, "writer")
                # Then: no result is kept
                self.assertIsNone(called.result(helpers.KEPT, "a1"))


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

    def test_routes_laid_that_lay_py_print_would_refuse_are_an_error_at_each_event(self):
        # Given: the laid routes fanning out reviewer with no order of its results, as no
        # `lay.py print` lets through
        laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
        laid["routes"] = {**laid["routes"], "fan_out": ["reviewer"]}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        for check, event, name in (
            (guard.check, self.start("writer"), "lead"),
            (guard.started, self.subagent("SubagentStart", "reviewer", "r1"), "reviewer"),
        ):
            with self.subTest(name=name):
                # When: lead starts writer, or reviewer starts
                told = self.told(check, event, name)
                # Then: it is an error of the laid file, the maker told to lay the routes again
                self.assertEqual(len(told), 1)
                self.assertTrue(told[0].error)
                self.assertEqual(
                    told[0].text,
                    f"lane cannot check the lanes of {name}: hooks/lanes.json gives reviewer in"
                    " `fan_out`, whose results `more` and `good` the routes do not order in"
                    " `precedence`, so the result of its runs at once could not be told. "
                    + LAY_AGAIN,
                )

    def test_kept_calls_that_cannot_be_read_are_an_error(self):
        # Given: lead's calls kept holding a line that is no entry
        called.keep(helpers.KEPT, "lead1", called.START)
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

    def test_a_routed_subagent_whose_file_has_no_step_is_told_its_result_has_none(self):
        # Given: reviewer, with no lane but its result commands, its file holding no step
        reviewer = os.path.join(self.plugin, "agents", "reviewer.md")
        self.write(
            reviewer, "---\nname: reviewer\ndescription: d\nbackground: true\n---\n\nReview.\n"
        )
        # When: it runs a command
        told = self.told(guard.check, self.bash("ls", "changelog:reviewer"), "reviewer")
        # Then: it is an error of its result, on step 0, a number no step has
        self.assertTrue(told[0].error)
        self.assertIn(
            "lane cannot check result on step 0 of reviewer: step 0 no longer", told[0].text
        )


# writer's result command `done`, as it reads it, given the plugin's folder.
DONE = "python3 {root}/hooks/lane/result.py writer done"
FORM = "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"
SCHEMA = {"type": "object", "required": ["version"], "properties": {"version": {"type": "string"}}}


def lane(kind: str, *takes: str, number: int = 3, **more: str) -> dict:
    """A step of the number laying the lane of the kind, taking the things."""
    return {"step": number, "lanes": [{"lane": kind, "takes": list(takes), **more}]}


class TestOrchestratorByName(GuardTest):
    def test_a_routed_subagent_named_before_the_orchestrator_is_none(self):
        # Given: routes from lead to editor, a name before lead's
        given = {
            "orchestrator": "lead",
            "step": 1,
            "routes": [{"from": "lead", "to": "editor"}, {"from": "editor", "on": "edited"}],
        }
        laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), {**laid, "routes": given})
        # When: editor starts, and reads a file
        start = self.subagent("SubagentStart", "editor", "e1")
        read = self.event("Read", {"file_path": "a.md"}, "changelog:editor", agent_id="e1")
        # Then: it is told nothing, as only lead follows the routes
        self.assertEqual(guard.started(self.plugin, "changelog", "editor", start, ""), [])
        self.assertEqual(guard.check(self.plugin, "changelog", "editor", read, ""), [])


class LanesTest(GuardTest):
    def given(self, text: str, agent: str = "a1") -> None:
        """writer's run of the ID given the prompt."""
        called.keep(helpers.KEPT, agent, called.given(text))

    def reading(self, path: str, tool: str = "Read") -> dict:
        """A PreToolUse event of writer reading the path, by Read or Grep."""
        given = {"file_path": path} if tool == "Read" else {"pattern": "x", "path": path}
        return self.event(tool, given)


class TestReadOnly(LanesTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay_lanes([lane("read_only", "CHANGELOG.md", "docs/", number=1)])

    def test_an_input_or_a_file_under_one_is_read_and_any_other_file_is_stopped(self):
        for event, through in (
            (self.reading("CHANGELOG.md"), True),
            (self.reading("docs/a.md", "Grep"), True),
            (self.reading("README.md"), False),
            (self.event("Grep", {"pattern": "x"}), False),
        ):
            with self.subTest(event=event):
                # Given: writer reading only CHANGELOG.md and docs/
                # When: it reads CHANGELOG.md, greps under docs/, reads another file, or greps the
                # folder it works in
                # Then: the inputs go through, and the rest is told the sentence
                said = [] if through else [guard.Said("Read only `CHANGELOG.md` or `docs/`.")]
                self.assertEqual(self.check(event), said)

    def test_the_form_of_an_in_form_lane_is_read_beside_the_inputs(self):
        # Given: writer reading only CHANGELOG.md, and writing entry.json in a form
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), SCHEMA)
        self.lay_lanes(
            [lane("read_only", "CHANGELOG.md", number=1), lane("in_form", "entry.json", FORM)]
        )
        # When: it reads the form, as the step names it
        # Then: it goes through
        form = os.path.join(self.plugin, "forms", "entry.json")
        self.assertEqual(self.check(self.reading(form)), [])

    def test_the_subagents_own_part_is_read_beside_the_inputs(self):
        # Given: writer reading only CHANGELOG.md and docs/, its steps in its part
        part = os.path.join(self.plugin, "prompts", "writer.md")
        self.write(part, self.read(self.agent_file).split("---\n\n", 1)[1])
        self.write(self.agent_file, helpers.PART_ENTRY.format(name="writer"))
        # When: it reads its part, which it was given whole as it started, or another part
        self.write(os.path.join(self.plugin, "prompts", "other.md"), "x\n")
        # Then: its own goes through, and the other is told the sentence
        self.assertEqual(self.check(self.reading(part)), [])
        said = [guard.Said("Read only `CHANGELOG.md` or `docs/`.")]
        other = os.path.join(self.plugin, "prompts", "other.md")
        self.assertEqual(self.check(self.reading(other)), said)

    def test_a_subagent_with_no_read_lane_reads_freely(self):
        # Given: writer with the README's lanes alone
        self.lay()
        # When: it reads any file
        # Then: it goes through
        self.assertEqual(self.check(self.reading("any.md")), [])


class TestInForm(LanesTest):
    def setUp(self) -> None:
        super().setUp()
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), SCHEMA)
        self.lay_lanes([lane("in_form", "entry.json", FORM)])
        self.sentence = f"Write `entry.json` in the form of `{FORM}`."

    def test_a_write_in_the_form_goes_through_and_one_out_of_it_is_told_the_point(self):
        for content, through in (('{"version": "1"}', True), ("{}", False)):
            with self.subTest(content=content):
                # Given: writer writing entry.json in the form
                # When: it writes it in the form, or out of it
                told = self.check(
                    self.event("Write", {"file_path": "entry.json", "content": content})
                )
                # Then: the first goes through, and the second is told the sentence and the point
                point = '$: expected the key "version", found an object without it'
                self.assertEqual(told, [] if through else [guard.Said(f"{self.sentence}\n{point}")])

    def test_a_write_of_another_file_goes_through_where_no_write_only_lane_holds_it(self):
        # Given: writer with in_form alone
        # When: it writes another file
        # Then: it goes through, as in_form holds the output alone to its form
        self.assertEqual(self.check(self.written("notes.md")), [])

    def test_a_form_gone_since_it_was_laid_is_an_error(self):
        # Given: the form removed
        os.remove(os.path.join(self.plugin, "forms", "entry.json"))
        # When: writer writes entry.json
        told = self.check(self.event("Write", {"file_path": "entry.json", "content": "{}"}))
        # Then: it is an error of in_form, telling to lay the lanes again
        self.assertTrue(told[0].error)
        self.assertIn(
            "lane cannot check in_form on step 3 of writer: `lay.py write` would now refuse it:"
            " in_form, which names the form",
            told[0].text,
        )
        self.assertIn("`lay.py write`", told[0].text)

    def test_an_in_form_lane_after_one_given_null_is_held(self):
        # Given: in_form on {work}, given null, and in_form on entry.json
        self.lay_lanes(
            [
                {
                    "step": 3,
                    "lanes": [
                        {"lane": "in_form", "takes": ["{work}", FORM]},
                        {"lane": "in_form", "takes": ["entry.json", FORM]},
                    ],
                }
            ]
        )
        self.given('{"work": null}')
        # When: writer writes entry.json out of the form
        told = self.check(self.event("Write", {"file_path": "entry.json", "content": "{}"}))
        # Then: the second is told, the first letting it through
        self.assertEqual([t.text.split("\n")[0] for t in told], [self.sentence])


class TestHold(LanesTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay_lanes(
            [
                {
                    "step": 2,
                    "lanes": [helpers.STEPS[0]["lanes"][0], lane("hold", "git push")["lanes"][0]],
                }
            ]
        )

    def test_a_held_command_is_put_to_the_person_with_its_sentence(self):
        # Given: writer holding git push for the person's approval
        # When: it runs git push
        # Then: it is asked of the person, with hold's sentence
        said = "Run `git push` only with the person's approval."
        self.assertEqual(self.check(self.bash("git push")), [guard.Said(said, ask=True)])

    def test_the_other_commands_go_on_as_run_only_says_and_any_other_is_told_both(self):
        # Given: writer running only git log --oneline, and holding git push
        # When: it runs git log --oneline, and git commit
        # Then: the first goes through, and the second is told both sentences and both commands
        self.assertEqual(self.check(self.bash("git log --oneline")), [])
        told = (
            f"{helpers.RUN}\nRun `git push` only with the person's approval.\n"
            "The commands you may run, each word for word: `git log --oneline`, `git push`."
        )
        self.assertEqual(self.check(self.bash("git commit")), [guard.Said(told)])


class TestOwnResults(LanesTest):
    """A subagent that gives results of its own, with no route from it, as the proposal's
    `results` names them, so a plugin that routes it, using this one, takes them."""

    def setUp(self) -> None:
        super().setUp()
        self.lay_lanes([lane("run_only", "git log --oneline", number=2)], results=["asks", "done"])
        self.gives = f"python3 {self.plugin}/hooks/lane/result.py writer"

    def test_each_result_goes_through_and_is_kept(self):
        # Given: writer giving `asks` or `done`
        # When: it runs the result command of `asks`
        # Then: it goes through, and the result is kept as it comes back
        self.assertEqual(self.check(self.bash(f"{self.gives} asks")), [])
        guard.came_back(
            self.plugin, "changelog", "writer", self.came_back(f"{self.gives} asks"), ""
        )
        self.assertEqual(called.result(helpers.KEPT, "a1"), "asks")

    def test_an_end_with_no_result_is_kept_going_once_with_both_commands(self):
        # Given: writer, which gave no result
        stop = self.subagent("SubagentStop", "writer", "a1")
        # When: it is about to end
        told = guard.stopping(self.plugin, "changelog", "writer", stop, "")
        # Then: it is kept going with the sentence of both commands
        said = f"End by running `{self.gives} asks` or `{self.gives} done`."
        self.assertEqual(told, [guard.Said(said)])


class TestEnd(LanesTest):
    def setUp(self) -> None:
        super().setUp()
        self.done = DONE.format(root=self.plugin)
        self.write("CHANGELOG.md", "one\ntwo\n")

    def ran(self, *calls: dict) -> None:
        """writer's run started, with the calls kept as they came back."""
        called.keep(helpers.KEPT, "a1", called.START)
        for c in calls:
            called.keep(helpers.KEPT, "a1", c)

    def test_the_result_command_goes_through_once_each_lane_of_the_end_holds(self):
        # Given: writer reading CHANGELOG.md whole, ending once it is made, and testing src/
        self.lay_lanes(
            [
                lane("read_whole", "CHANGELOG.md", number=1),
                lane("test_after", "src/", "make test", number=2),
                lane("end_when", "CHANGELOG.md", number=3),
            ]
        )
        # When: it runs the test, and gives its result having read CHANGELOG.md whole
        self.assertEqual(self.check(self.bash("make test")), [])
        self.ran(helpers.kept_call("Read", file_path="CHANGELOG.md"))
        # Then: the result goes through
        self.assertEqual(self.check(self.bash(self.done)), [])

    def test_a_result_with_work_missing_is_told_each_lanes_sentence_and_what_is_missing(self):
        self.write("review.md", "- B-1: a\n")
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), SCHEMA)
        self.write("entry.json", "{}")
        # Given: writer with a lane of each kind checked at the end, and in_form
        self.lay_lanes(
            [
                lane("read_whole", "CHANGELOG.md", number=1),
                lane("test_after", "src/", "make test", number=2),
                {
                    "step": 3,
                    "lanes": [
                        {"lane": "end_when", "takes": ["report.md"]},
                        {"lane": "in_form", "takes": ["entry.json", FORM]},
                    ],
                },
                lane("every_item", "review.md", number=4),
            ]
        )
        # When: it gives its result having read nothing, changed src/ untested and answered
        # nothing
        self.ran(helpers.kept_call("Write", file_path="src/a.py", content="x"))
        told = self.check(self.bash(self.done))
        # Then: each lane is told, with what is missing on the next line
        self.assertEqual(
            [t.text for t in told],
            [
                "Read `CHANGELOG.md` to its end.\n`CHANGELOG.md` unread from line 1",
                (
                    "After changing `src/`, pass `make test`.\n"
                    "`src/` changed with no test passed after"
                ),
                "End only once `report.md` is made.\n`report.md` not there",
                (
                    f"Write `entry.json` in the form of `{FORM}`.\n`entry.json`: $: expected the"
                    ' key "version", found an object without it'
                ),
                "Answer every item of `review.md`.\nB-1 of `review.md` unanswered",
            ],
        )

    def test_the_items_are_read_by_the_lanes_adapter_and_its_failure_is_an_error(self):
        self.write("review.md", "## Finding 1\n")
        for text, error in ((helpers.ITEMS_ADAPTER, False), ("import sys\nsys.exit(2)\n", True)):
            with self.subTest(error=error):
                # Given: every_item reading review.md by the plugin's items adapter, or one failing
                self.write(os.path.join(self.plugin, "hooks", "adapters", "items-f.py"), text)
                self.lay_lanes(
                    [lane("every_item", "review.md", number=4, adapter="hooks/adapters/items-f.py")]
                )
                # When: writer gives its result having answered nothing
                told = self.check(self.bash(self.done))
                # Then: F1 is unanswered, or the adapter's failure is an error naming it
                if error:
                    self.assertTrue(told[0].error)
                    self.assertIn("the adapter hooks/adapters/items-f.py exited 2", told[0].text)
                    self.assertIn("must fix its adapter hooks/adapters/items-f.py", told[0].text)
                else:
                    self.assertIn("F1 of `review.md` unanswered", told[0].text)

    def test_a_lane_of_the_end_after_one_given_null_is_checked(self):
        # Given: writer ending once {work} is made, given null, and once report.md is made
        self.lay_lanes([lane("end_when", "{work}", number=1), lane("end_when", "report.md")])
        self.given('{"work": null}')
        # When: it gives its result with report.md not made
        told = self.check(self.bash(self.done))
        # Then: the second is told
        self.assertEqual(
            [t.text for t in told], ["End only once `report.md` is made.\n`report.md` not there"]
        )

    def test_a_file_written_in_an_earlier_run_answers_no_item(self):
        self.write("review.md", "- B-1: a\n")
        self.write("answers.md", "B-1 fixed.")
        # Given: writer answering every item of review.md, its answers written in an earlier run
        self.lay_lanes([lane("every_item", "review.md", number=4)])
        self.ran(helpers.kept_call("Write", file_path="answers.md", content="B-1 fixed."))
        called.keep(helpers.KEPT, "a1", called.END)
        called.keep(helpers.KEPT, "a1", called.START)
        # When: it gives its result in the run after
        told = self.check(self.bash(self.done))
        # Then: B-1 is unanswered
        self.assertEqual(
            [t.text for t in told],
            ["Answer every item of `review.md`.\nB-1 of `review.md` unanswered"],
        )


class TestValues(LanesTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay_lanes([lane("write_only", "{work}")])

    def test_a_value_given_in_the_prompt_or_a_message_after_is_held_to(self):
        # Given: writer given notes.md as its work
        self.given(json.dumps({"work": "notes.md"}))
        # When: it writes notes.md, and another file
        # Then: notes.md goes through, and the other is told the sentence as the step says it
        self.assertEqual(self.check(self.written("notes.md")), [])
        self.assertEqual(self.check(self.written("a.md")), [guard.Said("Write only `{work}`.")])
        # And: once a message gives it a.md and b.md, those go through and notes.md does not
        called.keep(helpers.KEPT, "a1", called.message('{"work": ["a.md", "b.md", ""]}'))
        self.assertEqual(self.check(self.written("b.md")), [])
        self.assertEqual(self.check(self.written("notes.md")), [guard.Said("Write only `{work}`.")])

    def test_a_value_given_as_null_lets_the_lane_through(self):
        for kind, event in (("write_only", self.written("any.md")), ("run_only", self.bash("ls"))):
            with self.subTest(kind=kind):
                # Given: the lane taking {work}, the run given none
                self.lay_lanes([lane(kind, "{work}")])
                self.given('{"work": null}')
                # When: writer makes a call the lane judges
                # Then: it goes through
                self.assertEqual(self.check(event), [])

    def test_a_value_not_given_or_given_empty_is_an_error(self):
        for agent, given, said in (
            ("v1", "no JSON", "`{work}` was given no value"),
            ("v2", '{"work": [""]}', "`{work}` was given empty"),
        ):
            with self.subTest(given=given):
                # Given: a run of writer given no value, or an empty one
                called.keep(helpers.KEPT, agent, called.START)
                called.keep(helpers.KEPT, agent, called.given(given))
                # When: it writes a file
                write = {"file_path": "notes.md", "content": "x"}
                told = self.check(self.event("Write", write, agent_id=agent))
                # Then: it is an error of write_only, naming what is wrong
                self.assertTrue(told[0].error)
                self.assertIn(
                    f"lane cannot check write_only on step 3 of writer: {said}", told[0].text
                )

    def test_the_values_are_read_by_the_subagents_adapter(self):
        # Given: writer's values read by its adapter, given work=notes.md
        self.write(
            os.path.join(self.plugin, "hooks", "adapters", "values-w.py"), helpers.VALUES_ADAPTER
        )
        self.lay_lanes([lane("write_only", "{work}")], "hooks/adapters/values-w.py")
        self.given("work=notes.md")
        # When: it writes notes.md
        # Then: it goes through
        self.assertEqual(self.check(self.written("notes.md")), [])
        # And: the adapter failing is an error naming it
        self.write(os.path.join(self.plugin, "hooks", "adapters", "values-w.py"), "x(")
        told = self.check(self.written("notes.md"))
        self.assertIn("the adapter hooks/adapters/values-w.py exited 1", told[0].text)

    def test_a_value_given_as_null_lets_each_kind_of_lane_through(self):
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), SCHEMA)
        for steps, event in (
            ([lane("read_only", "{work}", number=1)], self.reading("any.md")),
            (
                [lane("read_only", "CHANGELOG.md", number=1), lane("in_form", "{work}", FORM)],
                self.reading("CHANGELOG.md"),
            ),
            ([lane("in_form", "{work}", FORM)], self.written("entry.json")),
            ([lane("end_when", "{work}")], self.bash(DONE.format(root=self.plugin))),
        ):
            with self.subTest(steps=steps):
                # Given: read_only, in_form, or end_when taking {work}, the run given none
                self.lay_lanes(steps)
                self.given('{"work": null}')
                # When: writer makes a call the lane judges
                # Then: it goes through
                self.assertEqual(self.check(event), [])

    def test_the_values_are_read_once_for_lanes_taking_them_together(self):
        # Given: two write_only lanes taking values, read by the subagent's adapter, which counts
        # its runs
        script = os.path.join(self.plugin, "hooks", "adapters", "values-w.py")
        self.write(script, helpers.VALUES_ADAPTER + "open('runs', 'a').write('x')\n")
        steps = [lane("write_only", "{work}"), lane("write_only", "{more}", number=2)]
        self.lay_lanes(steps, "hooks/adapters/values-w.py")
        self.given("work=a.md\nmore=b.md")
        # When: writer writes b.md
        # Then: it goes through, the adapter run once
        self.assertEqual(self.check(self.written("b.md")), [])
        self.assertEqual(self.read("runs"), "x")

    def test_a_value_of_several_texts_stays_in_the_place_of_its_take(self):
        # Given: in_form holding {work} to the form, the run given two outputs
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), SCHEMA)
        self.lay_lanes([lane("in_form", "{work}", FORM)])
        self.given('{"work": ["a.json", "b.json"]}')
        # When: writer writes the second out of the form
        told = self.check(self.event("Write", {"file_path": "b.json", "content": "{}"}))
        # Then: it is told the sentence and the point, the form held as the lane names it
        self.assertEqual(len(told), 1)
        self.assertTrue(told[0].text.startswith(f"Write `{{work}}` in the form of `{FORM}`.\n$:"))

    def test_a_form_given_as_a_value_that_cannot_be_read_is_an_error(self):
        # Given: in_form holding entry.json to the form the run gives, given one not there
        self.lay_lanes([lane("in_form", "entry.json", "{form}")])
        self.given('{"form": "forms/none.json"}')
        # When: writer writes entry.json
        told = self.check(self.event("Write", {"file_path": "entry.json", "content": "{}"}))
        # Then: it is an error naming the form, as `lay.py write` would refuse it laid so
        self.assertTrue(told[0].error)
        self.assertIn(
            "lane cannot check in_form on step 3 of writer: names the form forms/none.json",
            told[0].text,
        )

    def test_a_lane_laid_out_of_its_in_is_an_error_whatever_its_values(self):
        # Given: in_form taking its output and form from one value, given one text
        self.lay_lanes([lane("in_form", "{entry}")])
        self.given('{"entry": "entry.json"}')
        # When: writer writes a file
        told = self.check(self.written("entry.json"))
        # Then: it is an error, as `lay.py write` would refuse the lane, naming the place
        self.assertIn(
            "would now refuse it: in_form takes out of its places at $.form", told[0].text
        )


class TestValueInCommand(LanesTest):
    """A command holding the run's value as one part."""

    TAKE = "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py {file}"

    def setUp(self) -> None:
        super().setUp()
        self.lay_lanes([lane("run_only", self.TAKE, number=2)])
        self.check_of = f"python3 {self.plugin}/scripts/check.py"

    def test_the_command_with_the_runs_value_goes_through_and_another_is_told_it(self):
        # Given: writer given `my notes.json` as its file
        self.given('{"file": "my notes.json"}')
        # When: it runs the check on it as one word, on it as two, and on another file
        # Then: the first goes through, and the others are told the sentence as the step says it,
        # and the command with the value put in
        self.assertEqual(self.check(self.bash(f"{self.check_of} 'my notes.json'")), [])
        told = [
            guard.Said(
                f"Run only `{self.TAKE}`.\nThe commands you may run, each word for word:"
                f" `{self.check_of} 'my notes.json'`."
            )
        ]
        for command in (f"{self.check_of} my notes.json", f"{self.check_of} other.json"):
            with self.subTest(command=command):
                self.assertEqual(self.check(self.bash(command)), told)

    def test_a_value_given_as_null_lets_the_lane_through_and_none_given_is_an_error(self):
        for agent, text, through in (("v1", '{"file": null}', True), ("v2", "{}", False)):
            with self.subTest(text=text):
                # Given: a run of writer given null as its file, or no file
                called.keep(helpers.KEPT, agent, called.START)
                called.keep(helpers.KEPT, agent, called.given(text))
                # When: it runs any command
                told = self.check(self.event("Bash", {"command": "ls"}, agent_id=agent))
                # Then: it goes through, or is an error naming the value
                if through:
                    self.assertEqual(told, [])
                else:
                    self.assertIn(
                        "lane cannot check run_only on step 2 of writer: `{file}` was given no"
                        " value",
                        told[0].text,
                    )

    def test_a_held_command_and_a_test_hold_their_value_too(self):
        # Given: writer holding a push of its branch, and testing src/ by the check of its file
        self.lay_lanes(
            [
                lane("hold", "git push origin {branch}", number=2),
                lane("test_after", "src/", self.TAKE, number=3),
            ]
        )
        self.given('{"branch": "work", "file": "a.json"}')
        called.keep(helpers.KEPT, "a1", called.START)
        called.keep(
            helpers.KEPT, "a1", helpers.kept_call("Write", file_path="src/a.py", content="x")
        )
        # When: it pushes its branch, and another
        # Then: its own is put to the person, and the other is stopped
        said = "Run `git push origin {branch}` only with the person's approval."
        self.assertEqual(
            self.check(self.bash("git push origin work")), [guard.Said(said, ask=True)]
        )
        self.assertFalse(self.check(self.bash("git push origin main"))[0].ask)
        # And: its result counts the test passed only by the check of its own file
        done = DONE.format(root=self.plugin)
        for command, missing in (
            (f"{self.check_of} b.json", True),
            (f"{self.check_of} a.json", False),
        ):
            with self.subTest(command=command):
                called.keep(helpers.KEPT, "a1", helpers.kept_call("Bash", command=command))
                told = self.check(self.bash(done))
                self.assertEqual(bool(told), missing)


# What a values adapter answers, giving writer a.md as its work.
VALUES = '{"values": {"work": ["a.md"]}}'


class TestAdapterTime(LanesTest):
    def timeout(self, event: dict, answer: str) -> float:
        """The seconds the adapter is given on the event, the clock at 1000 seconds, long after
        lane's code was loaded, the adapter answering the answer."""
        done = subprocess.CompletedProcess([], 0, answer, "")
        clock = mock.patch("time.monotonic", return_value=1000.0)
        with clock, mock.patch.object(subprocess, "run", return_value=done) as run:
            self.check(event)
        return run.call_args.kwargs["timeout"]

    def test_an_adapter_is_left_the_hooks_time_counted_from_the_event(self):
        # Given: writer's values read by its adapter, and review.md's items by another
        self.write("review.md", "## Finding 1\n")
        values = "hooks/adapters/values-w.py"
        items = lane("every_item", "review.md", number=4, adapter="hooks/adapters/items-f.py")
        for steps, adapter, event, answer in (
            ([lane("write_only", "{work}")], values, self.written("a.md"), VALUES),
            ([items], None, self.bash(DONE.format(root=self.plugin)), '{"items": []}'),
        ):
            with self.subTest(event=event):
                self.lay_lanes(steps, adapter)
                self.given("work=a.md")
                # When: the guard begins on an event long after lane's code was loaded, as in a
                # process that handles many
                # Then: each adapter is left the hook's whole 8 seconds
                self.assertEqual(self.timeout(event, answer), 8.0)


class TestPart(LanesTest):
    def setUp(self) -> None:
        super().setUp()
        self.part = os.path.join(self.plugin, "prompts", "writer.md")
        entry = helpers.PART_ENTRY.format(name="writer")
        self.write(
            self.part, helpers.LAID.split("---\n\n", 1)[1] + "Run `${CLAUDE_PLUGIN_ROOT}/x`.\n"
        )
        self.write(self.agent_file, entry)

    def test_a_subagent_with_lanes_is_given_its_part_whole_as_it_starts(self):
        # Given: writer's entry naming its part, where its lanes' sentences are
        # When: writer starts
        told = guard.started(
            self.plugin, "changelog", "writer", self.subagent("SubagentStart", "writer", "a1"), ""
        )
        # Then: it is given the part whole, the plugin's folder put in
        text = self.read(self.part).replace("${CLAUDE_PLUGIN_ROOT}", self.plugin)
        self.assertEqual(told, [guard.Said(text, plain=True)])
        # And: its lanes are read from the part
        self.assertEqual(self.check(self.bash("git log --oneline")), [])

    def test_a_part_not_there_is_an_error(self):
        # Given: the part removed
        os.remove(self.part)
        # When: writer starts
        told = guard.started(
            self.plugin, "changelog", "writer", self.subagent("SubagentStart", "writer", "a1"), ""
        )
        # Then: it is an error of its lanes, naming the part
        self.assertTrue(told[0].error)
        self.assertIn(
            "lane cannot check the lanes of writer: its part prompts/writer.md is not there",
            told[0].text,
        )


class TestHanded(LanesTest):
    def agent_call(
        self,
        held: str,
        kind: str = "changelog:writer",
        prompt: str = '{"work": "notes.md"}',
        **more,
    ) -> dict:
        """The main conversation's Agent call starting the subagent of the type with the prompt."""
        given = {"description": "d", "prompt": prompt, "subagent_type": kind}
        return {**self.event("Agent", given, None, held), "tool_use_id": "t1", **more}

    def launched(self, agent: str, prompt: str = '{"work": "notes.md"}', **more) -> None:
        """The main conversation's start of writer comes back launched in the background as the
        run of the ID."""
        back = helpers.back(agent, "async_launched")
        event = self.agent_call("PostToolUse", prompt=prompt, tool_response=back, **more)
        guard.handed("changelog", event, "PostToolUse")

    def test_a_start_come_back_gives_its_prompt_to_the_run_of_the_id_it_gives(self):
        for status in ("async_launched", "completed"):
            with self.subTest(status=status):
                # Given: the main conversation's Agent call starting writer, made
                guard.handed("changelog", self.agent_call("PreToolUse"), "PreToolUse")
                # Then: no run is given its prompt as it is made
                self.assertIsNone(called.texts(helpers.KEPT, f"a{status}"))
                # When: it comes back with the ID of the run it started
                back = helpers.back(f"a{status}", status)
                event = self.agent_call("PostToolUse", tool_response=back)
                guard.handed("changelog", event, "PostToolUse")
                # Then: that run is given the call's prompt
                self.assertEqual(called.texts(helpers.KEPT, f"a{status}"), ['{"work": "notes.md"}'])

    def test_runs_of_one_subagent_at_once_are_each_given_their_own_prompt(self):
        # Given: two starts of writer at once, with differing prompts, coming back in turn
        self.launched("a1", '{"work": "a.md"}')
        self.launched("a2", '{"work": "b.md"}')
        # Then: each run is given its own
        self.assertEqual(called.texts(helpers.KEPT, "a1"), ['{"work": "a.md"}'])
        self.assertEqual(called.texts(helpers.KEPT, "a2"), ['{"work": "b.md"}'])

    def test_a_start_that_failed_or_gave_back_no_id_gives_no_run_its_prompt(self):
        for held, back in (
            ("PostToolUseFailure", helpers.back("f1")),
            ("PostToolUse", {"status": "async_launched"}),
            ("PostToolUse", {"status": "async_launched", "agentId": "a/b"}),
            ("PostToolUse", "x"),
        ):
            with self.subTest(held=held, back=back):
                # Given: writer's start failed, its event holding a run's ID, or come back with no
                # ID, an ID that could name a file elsewhere, or no object
                event = self.agent_call(held, tool_response=back)
                # When: it is handed on
                guard.handed("changelog", event, held)
                # Then: no run is given its prompt
                self.assertFalse(os.path.exists(os.path.join(self.base, "lane")))

    def test_a_message_is_kept_as_its_call_is_made_alone(self):
        # Given: writer's run given its prompt
        self.launched("a1")
        sent = {"to": "a1", "message": '{"work": "a.md"}'}
        for held, tool in (("PostToolUse", "SendMessage"), ("PreToolUse", "Write")):
            # When: a SendMessage call to it comes back, or another tool's call of the same input
            # is made
            event = {**self.event(tool, sent, None, held), "tool_use_id": "t9"}
            guard.handed("changelog", event, held)
        # Then: no message is kept, as one is kept as its SendMessage call is made
        self.assertEqual(called.texts(helpers.KEPT, "a1"), ['{"work": "notes.md"}'])

    def test_a_message_to_a_run_of_no_calls_kept_makes_no_folder(self):
        # Given: nothing kept in the session
        # When: a SendMessage call is made to a run
        sent = {"to": "a1", "message": "m"}
        event = {**self.event("SendMessage", sent, None), "tool_use_id": "t9"}
        guard.handed("changelog", event, "PreToolUse")
        # Then: no folder is made for the session
        self.assertFalse(os.path.exists(os.path.join(self.base, "lane")))

    def test_a_message_sent_to_a_run_is_kept_after_its_prompt(self):
        # Given: writer's run given its prompt
        self.launched("a1")
        # When: a SendMessage call is made to it, and one to a run of no calls kept
        for to in ("a1", "z9", "a b"):
            sent = {"to": to, "message": '{"work": "a.md"}'}
            guard.handed(
                "changelog",
                {**self.event("SendMessage", sent, None), "tool_use_id": "t9"},
                "PreToolUse",
            )
        # Then: the message is kept after the prompt, and nothing for the other
        self.assertEqual(
            called.texts(helpers.KEPT, "a1"), ['{"work": "notes.md"}', '{"work": "a.md"}']
        )
        self.assertEqual(called.kept(helpers.KEPT, "z9"), [])

    def test_a_call_of_another_plugin_or_out_of_its_fields_keeps_nothing(self):
        back = helpers.back("a1", "async_launched")
        for event in (
            self.agent_call("PostToolUse", kind="other:writer", tool_response=back),
            {
                **self.agent_call("PostToolUse", tool_response=back),
                "tool_input": {"subagent_type": "changelog:writer"},
            },
            self.agent_call("PostToolUse", tool_response=back, tool_use_id=1),
            self.agent_call("PostToolUse", tool_response=back, session_id="a/b"),
            {**self.agent_call("PostToolUse", tool_response=back), "tool_input": "x"},
            {**self.event("Read", {"file_path": "x"}, None, "PostToolUse"), "tool_use_id": "t1"},
        ):
            with self.subTest(event=event):
                # Given: an Agent call of another plugin, one of no prompt, of no ID, of a session
                # no ID names, of no input, or another tool's call, come back
                # When: it is handed on
                guard.handed("changelog", event, "PostToolUse")
                # Then: writer's run is given nothing
                self.assertFalse(os.path.exists(os.path.join(self.base, "lane")))


class TestJoined(LanesTest):
    """A run's call waits a short time for the start's ID to come back, as the run starts before
    its start comes back."""

    def setUp(self) -> None:
        super().setUp()
        self.lay_lanes([lane("write_only", "{work}")])

    def test_a_call_made_before_its_start_came_back_waits_for_it(self):
        for back in (3, 60):
            with self.subTest(back=back):
                # Given: writer's run, whose start comes back with its prompt as the guard waits,
                # in the third look's step or the last's
                called.keep(helpers.KEPT, f"r{back}", called.START)

                def comes_back(_: float, agent: str = f"r{back}", at: int = back) -> None:
                    if sleep.call_count == at:
                        called.keep(helpers.KEPT, agent, called.given('{"work": "notes.md"}'))

                with mock.patch.object(guard.time, "sleep", side_effect=comes_back) as sleep:
                    # When: it writes notes.md before its start has come back
                    write = self.event("Write", {"file_path": "notes.md"}, agent_id=f"r{back}")
                    told = self.check(write)
                # Then: the guard waited in steps of 0.05 seconds until the prompt came, and the
                # write goes through
                self.assertEqual(told, [])
                self.assertEqual(sleep.call_args_list, [mock.call(0.05)] * back)

    def test_a_call_whose_start_never_came_back_is_stopped_after_the_wait(self):
        # Given: writer's run, whose start never comes back
        with mock.patch.object(guard.time, "sleep") as sleep:
            # When: it writes notes.md
            told = self.check(self.written("notes.md"))
        # Then: the guard waited 3 seconds in steps of 0.05, and the call is stopped with an error
        # saying why and who must fix it
        self.assertEqual(sleep.call_args_list, [mock.call(0.05)] * 60)
        self.assertTrue(told[0].error)
        self.assertEqual(
            told[0].text,
            "lane cannot check write_only on step 3 of writer: the Agent call starting it gave"
            " back no ID of its run within 3 seconds, so what it was given is not known. Ask the"
            " main conversation for the fix: whoever starts writer must start it with the Agent"
            " tool, and where they did, Claude Code must be updated with `claude update`, and"
            " where this goes on, it must be reported at https://github.com/lovaizu/ccpm/issues."
            " Go on with the rest of your work meanwhile.",
        )

    def test_the_wait_is_kept_within_the_hooks_time(self):
        # Given: the guard begun on the event 7 of the hook's 8 seconds ago
        clock = iter([0.0, 7.0])
        later = mock.patch.object(guard.time, "monotonic", side_effect=lambda: next(clock, 7.0))
        with later, mock.patch.object(guard.time, "sleep") as sleep:
            # When: writer writes before its start has come back
            self.check(self.written("notes.md"))
        # Then: it waits only the second left
        self.assertEqual(sleep.call_count, 20)

    def test_a_call_needing_no_value_does_not_wait(self):
        # Given: writer with lanes taking no value
        self.lay()
        with mock.patch.object(guard.time, "sleep") as sleep:
            # When: it runs a command before its start has come back
            told = self.check(self.bash("git log --oneline"))
        # Then: it goes through at once
        self.assertEqual((told, sleep.call_count), ([], 0))

    def test_runs_of_one_subagent_at_once_are_each_held_to_their_own_values(self):
        # Given: two runs of writer at once, given a.md and b.md
        self.given('{"work": "a.md"}', "a1")
        self.given('{"work": "b.md"}', "a2")
        for agent, mine, other in (("a1", "a.md", "b.md"), ("a2", "b.md", "a.md")):
            with self.subTest(agent=agent):
                # When: each writes its own file, and the other's
                write = {"file_path": mine, "content": "x"}
                theirs = {"file_path": other, "content": "x"}
                # Then: its own goes through, and the other's is stopped
                self.assertEqual(self.check(self.event("Write", write, agent_id=agent)), [])
                self.assertEqual(
                    self.check(self.event("Write", theirs, agent_id=agent)),
                    [guard.Said("Write only `{work}`.")],
                )


class TestBackground(GuardTest):
    def test_a_subagent_whose_file_no_longer_sets_background_is_an_error(self):
        for held, check, event in (
            ("PreToolUse", guard.check, self.bash("git log --oneline")),
            ("SubagentStart", guard.started, self.subagent("SubagentStart", "writer", "a1")),
        ):
            with self.subTest(held=held):
                # Given: writer laid, its file since set to run in the foreground
                self.write(
                    self.agent_file, helpers.LAID.replace("background: true", "background: false")
                )
                # When: it starts, or runs a command its lanes name
                told = check(self.plugin, "changelog", "writer", event, "")
                # Then: it is an error of its lanes, telling to set it again
                self.assertTrue(told[0].error)
                self.assertEqual(
                    told[0].text,
                    "lane cannot check the lanes of writer: its file agents/writer.md no longer"
                    " sets `background: true`, so lane cannot tell its runs apart. Ask the main"
                    " conversation for the fix: the maker of changelog must set `background:"
                    " true` in the frontmatter of agents/writer.md again. Go on with the rest of"
                    " your work meanwhile.",
                )


if __name__ == "__main__":
    unittest.main()
