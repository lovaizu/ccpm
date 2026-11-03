"""The guard: of a tool call of a subagent with lanes laid, whether it goes through or which
sentences stop it, judged from the call's documented input alone; of a subagent the routes name,
each start of the orchestrator's and each result given, the next start told as it starts and as
each start comes back, and an end kept going while it is due or no result is given; and, where it
cannot judge, the error that says why and who must fix it."""

import json
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


# writer's result command `done`, as it reads it, given the plugin's folder.
DONE = "python3 {root}/hooks/lane/result.py writer done"
FORM = "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"
SCHEMA = {"type": "object", "required": ["version"], "properties": {"version": {"type": "string"}}}


def lane(kind: str, *takes: str, number: int = 3, **more: str) -> dict:
    """A step of the number laying the lane of the kind, taking the things."""
    return {"step": number, "lanes": [{"lane": kind, "takes": list(takes), **more}]}


class LanesTest(GuardTest):
    def given(self, text: str, agent: str = "a1") -> None:
        """writer's run of the ID given the prompt."""
        called.keep("s1", agent, called.given(text))

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
        self.assertIn("lane cannot check in_form on step 3 of writer: names the form", told[0].text)
        self.assertIn("`lay.py write`", told[0].text)


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


class TestEnd(LanesTest):
    def setUp(self) -> None:
        super().setUp()
        self.done = DONE.format(root=self.plugin)
        self.write("CHANGELOG.md", "one\ntwo\n")

    def ran(self, *calls: dict) -> None:
        """writer's run started, with the calls kept as they came back."""
        called.keep("s1", "a1", called.START)
        for c in calls:
            called.keep("s1", "a1", c)

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
        called.keep("s1", "a1", called.message('{"work": ["a.md", "b.md", ""]}'))
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

    def test_a_value_not_given_given_empty_or_unknown_is_an_error(self):
        for given, said in (
            ("no JSON", "`{work}` was given no value"),
            ('{"work": [""]}', "`{work}` was given empty"),
            (None, "two starts of it with differing prompts were waiting as it started"),
        ):
            with self.subTest(given=given):
                # Given: writer's run given no value, an empty one, or a prompt it cannot tell
                called.keep("s1", "a1", called.START)
                called.keep("s1", "a1", called.given(given))
                # When: it writes a file
                told = self.check(self.written("notes.md"))
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

    def test_values_putting_a_lane_out_of_its_in_is_an_error(self):
        # Given: in_form taking its output and form from one value, given one text
        self.lay_lanes([lane("in_form", "{entry}")])
        self.given('{"entry": "entry.json"}')
        # When: writer writes a file
        told = self.check(self.written("entry.json"))
        # Then: it is an error, naming the place out of the IN
        self.assertIn("what it is given is out of its IN at $.takes.form", told[0].text)


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
        self, held: str, kind: str = "changelog:writer", use: str = "t1", **more
    ) -> dict:
        """The main conversation's Agent call of the ID starting the subagent of the type."""
        given = {"description": "d", "prompt": '{"work": "notes.md"}', "subagent_type": kind}
        return {**self.event("Agent", given, None, held), "tool_use_id": use, **more}

    def run_start(self, agent: str = "a1") -> None:
        """writer's run of the ID starts."""
        guard.started(
            self.plugin, "changelog", "writer", self.subagent("SubagentStart", "writer", agent), ""
        )

    def test_a_start_takes_the_prompt_of_the_agent_call_made_for_it(self):
        # Given: the main conversation's Agent call starting writer
        guard.handed("changelog", self.agent_call("PreToolUse"), "PreToolUse")
        # When: writer starts
        self.run_start()
        # Then: its run is given the call's prompt
        self.assertEqual(called.texts("s1", "a1"), ['{"work": "notes.md"}'])
        # And: a later start takes no prompt already taken
        self.run_start("a2")
        self.assertEqual(called.texts("s1", "a2"), [])

    def test_two_calls_waiting_with_differing_prompts_leave_the_start_unable_to_tell(self):
        # Given: two Agent calls of writer waiting, with differing prompts
        guard.handed("changelog", self.agent_call("PreToolUse"), "PreToolUse")
        other = self.agent_call("PreToolUse", use="t2")
        other["tool_input"]["prompt"] = "other"
        guard.handed("changelog", other, "PreToolUse")
        # When: writer starts
        self.run_start()
        # Then: it cannot tell its prompt
        self.assertIsNone(called.texts("s1", "a1"))
        # And: the call coming back with the run's ID gives it its own
        back = self.agent_call("PostToolUse", tool_response=helpers.back("a1"))
        guard.handed("changelog", back, "PostToolUse")
        self.assertEqual(called.texts("s1", "a1"), ['{"work": "notes.md"}'])

    def test_a_call_come_back_or_failed_is_no_longer_waiting(self):
        for held in ("PostToolUse", "PostToolUseFailure"):
            with self.subTest(held=held):
                # Given: writer's Agent call come back, launched with no ID, or failed
                guard.handed("changelog", self.agent_call("PreToolUse", use=held), "PreToolUse")
                guard.handed("changelog", self.agent_call(held, use=held, tool_response="x"), held)
                # When: a run of writer starts
                self.run_start(f"r{held}")
                # Then: it takes no prompt
                self.assertEqual(called.texts("s1", f"r{held}"), [])

    def test_a_message_sent_to_a_run_is_kept_after_its_prompt(self):
        # Given: writer's run given its prompt
        guard.handed("changelog", self.agent_call("PreToolUse"), "PreToolUse")
        self.run_start()
        # When: a SendMessage call is made to it, and one to a run of no calls kept
        for to in ("a1", "z9", "a b"):
            sent = {"to": to, "message": '{"work": "a.md"}'}
            guard.handed(
                "changelog",
                {**self.event("SendMessage", sent, None), "tool_use_id": "t9"},
                "PreToolUse",
            )
        # Then: the message is kept after the prompt, and nothing for the other
        self.assertEqual(called.texts("s1", "a1"), ['{"work": "notes.md"}', '{"work": "a.md"}'])
        self.assertEqual(called.kept("s1", "z9"), [])

    def test_a_call_of_another_plugin_or_out_of_its_fields_keeps_nothing(self):
        for event in (
            self.agent_call("PreToolUse", kind="other:writer"),
            {**self.agent_call("PreToolUse"), "tool_input": {"subagent_type": "changelog:writer"}},
            {**self.agent_call("PreToolUse"), "tool_use_id": 1},
            {**self.agent_call("PreToolUse"), "session_id": "a/b"},
            {**self.event("Read", {"file_path": "x"}, None), "tool_use_id": "t1"},
        ):
            with self.subTest(event=event):
                # Given: an Agent call of another plugin, one of no prompt, of no ID, of a session
                # no ID names, or another tool's call
                guard.handed("changelog", event, "PreToolUse")
                # When: writer starts
                self.run_start()
                # Then: its run is given nothing
                self.assertEqual(called.texts("s1", "a1"), [])


if __name__ == "__main__":
    unittest.main()
