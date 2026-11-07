"""The guard: of a tool call of a subagent with lanes laid, whether it goes through or which
sentences stop it, judged from the call's documented input alone; of a subagent the routes name,
each result given, and its end kept going while no result is given; of the main conversation, a
run of the skill the routes name begun, each start of it checked and told the wait, each end told
the next start, and the end of a turn kept going once while a start is due; and, where it cannot
judge, the error that says why and who must fix it."""

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
# The same, as the main conversation is told it, to tell the user.
LAY_AGAIN_MAIN = (
    "Tell the user: the maker of changelog must lay its lanes again with `lay.py write`, so they"
    " match its steps."
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

    def test_a_subagent_with_no_run_only_lane_runs_any_command(self):
        for laid, text in (
            ([helpers.STEPS[1]], helpers.LAID.replace(f" {helpers.RUN}", "")),
            (
                [{"step": 2, "lanes": [{"lane": "hold", "takes": ["git push"]}]}],
                helpers.WRITER.replace(
                    "--oneline`.\n", "--oneline`. Run `git push` only with the person's approval.\n"
                ),
            ),
        ):
            with self.subTest(laid=laid):
                # Given: writer with write_only alone laid, or hold alone
                self.lay(laid, text)
                # When: it runs a command no lane names
                # Then: it goes through
                self.assertEqual(self.check(self.bash("git commit -m entries")), [])


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

    def test_a_start_of_a_subagent_of_the_plugin_is_stopped(self):
        for given in (
            {"prompt": "p", "subagent_type": "changelog:reviewer"},
            {"prompt": "p", "subagent_type": "changelog:writer"},
        ):
            with self.subTest(given=given):
                # Given: writer with its lanes laid
                # When: it starts a subagent of changelog, another or itself
                told = self.check(self.event("Agent", given))
                # Then: the start is stopped, as the main conversation alone starts one
                self.assertEqual([t.text for t in told], [guard.MAIN_STARTS])

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
        """The subagent of the name and ID started, gave the result and ended."""
        self.told(guard.started, self.subagent("SubagentStart", name, agent_id), name)
        command = f"python3 {self.plugin}/hooks/lane/result.py {name} {on}"
        self.told(guard.came_back, self.came_back(command, f"changelog:{name}", agent_id), name)
        self.told(guard.stopping, self.subagent("SubagentStop", name, agent_id), name)

    def main(self, event: dict, wrong: str = "") -> list:
        """What the main conversation is told of the event, by the guard's check of its kind."""
        return guard.MAIN[event["hook_event_name"]](self.plugin, "changelog", event, wrong)

    def begun(self) -> list:
        """The run begun by `/changelog:write` typed: what the main conversation is told."""
        return self.main(self.expansion())

    def launched(self, name: str, agent_id: str) -> list:
        """The main conversation's start of the subagent of the name: what its PreToolUse is told,
        then, launched in the background with the ID, what its PostToolUse is told."""
        before = self.main(self.start(name))
        return before + self.main(self.start(name, "PostToolUse", helpers.back(agent_id, LAUNCHED)))

    def through(self, name: str, agent_id: str, on: str) -> list:
        """The subagent of the name started by the main conversation, giving the result and ending,
        and its task-notification reaching the main conversation: what that is told."""
        self.launched(name, agent_id)
        self.ran(name, agent_id, on)
        return self.main(self.notified(agent_id))


# What an Agent call of a subagent run in the background gives back as its status.
LAUNCHED = "async_launched"
WAIT_WRITER = "Wait for `changelog:writer` to end: you are told the next start once it has."


class TestRunBegun(RoutedTest):
    def test_the_skills_command_typed_begins_the_run_telling_the_first_start(self):
        # Given: the routes laid from write
        # When: `/changelog:write` is typed, and again while the run is on
        first, again = self.begun(), self.begun()
        # Then: the first start is told, and the second begins no run
        self.assertEqual(first, [guard.Said("Start `changelog:writer`.")])
        self.assertEqual(again, [])

    def test_the_skill_called_by_an_ai_begins_the_run_telling_the_first_start(self):
        # Given: the routes laid from write
        # When: the Skill call of changelog:write comes back
        told = self.main(self.skill_call("changelog:write", "PostToolUse"))
        # Then: the first start is told
        self.assertEqual(told, [guard.Said("Start `changelog:writer`.")])

    def test_another_command_or_skill_begins_no_run(self):
        for event in (
            self.expansion("changelog:other"),
            self.expansion("other:write"),
            self.skill_call("other:write", "PostToolUse"),
            {**self.skill_call("changelog:write", "PostToolUse"), "tool_response": "done"},
        ):
            with self.subTest(event=event):
                # Given: the routes laid from write
                # When: another command is typed, another skill called, or a Skill call comes
                # back with no commandName
                # Then: nothing is told, and no run begins
                self.assertEqual(self.main(event), [])
                self.assertFalse(called.begun(helpers.KEPT))

    def test_outside_a_run_nothing_of_the_main_conversation_is_touched(self):
        # Given: the routes laid, and no run begun
        # When: the main conversation starts reviewer, its start comes back, it is prompted, and
        # it ends its turn
        told = [
            self.main(self.start("reviewer")),
            self.main(self.start("reviewer", "PostToolUse", helpers.back("r1", LAUNCHED))),
            self.main(self.prompt()),
            self.main(self.turn()),
        ]
        # Then: nothing is told, and nothing is kept
        self.assertEqual(told, [[], [], [], []])
        self.assertEqual(called.kept(helpers.KEPT, called.RUN), [])

    def test_with_no_routes_laid_the_main_conversation_is_never_held(self):
        # Given: the README's lanes alone laid
        self.lay()
        # When: `/changelog:write` is typed
        # Then: nothing is told
        self.assertEqual(self.begun(), [])

    def test_an_event_with_no_session_is_left_alone(self):
        # Given: the routes laid
        # When: the command's expansion comes with no session, or one no ID names
        for session in (None, "../x"):
            event = {**self.expansion(), "session_id": session}
            # Then: nothing is told
            self.assertEqual(self.main(event), [])


class TestStarts(RoutedTest):
    def setUp(self) -> None:
        super().setUp()
        self.begun()

    def test_the_start_due_goes_through_and_any_other_start_is_stopped_with_it(self):
        for event, told in (
            (self.start("writer"), []),
            (self.start("reviewer"), [guard.Said(helpers.FOLLOW), guard.Said(START_WRITER)]),
            (self.start("planner"), [guard.Said(helpers.FOLLOW), guard.Said(START_WRITER)]),
            (self.start("checker:examiner"), []),
            (self.event("Agent", {"prompt": "p", "subagent_type": "Explore"}, None), []),
            (self.bash("git commit", None), []),
            (self.skill_call("other:check"), []),
        ):
            with self.subTest(event=event["tool_input"]):
                # Given: the run begun, writer due
                # When: the main conversation starts writer, reviewer, a subagent of changelog
                # the routes do not name, another plugin's subagent, makes another call, or calls
                # a skill the routes do not name
                # Then: only a start of changelog's other than writer is stopped, told the
                # sentence and the start due; the user's own calls go on
                self.assertEqual(self.main(event), told)

    def test_each_start_coming_back_tells_the_wait_and_each_end_the_next_start(self):
        # Given: the run begun, writer due
        # When: writer is started, gives `written` and ends, and its end reaches the main
        # conversation
        started = self.launched("writer", "w1")
        meanwhile = self.main(self.start("reviewer"))
        self.ran("writer", "w1", "written")
        told = self.main(self.notified("w1"))
        # Then: the start is told to wait, a start meanwhile is stopped with the wait, and the
        # end tells the next start by the result given
        self.assertEqual(started, [guard.Said(WAIT_WRITER)])
        self.assertEqual(meanwhile, [guard.Said(helpers.FOLLOW), guard.Said(WAIT_WRITER)])
        self.assertEqual(told, [guard.Said("writer gave `written`. Start `changelog:reviewer`.")])

    def test_a_route_that_starts_no_more_ends_the_run_once_told(self):
        # Given: writer gave `written`
        self.through("writer", "w1", "written")
        # When: reviewer gives `good`, and its end reaches the main conversation, then another
        # prompt
        told = self.through("reviewer", "r1", "good")
        again = self.main(self.prompt())
        # Then: no more starts are told, once, and the run is over: a start goes on, and an end
        # of a turn is let end
        self.assertEqual(told, [guard.Said("reviewer gave `good`. Start no more subagents.")])
        self.assertEqual(again, [])
        self.assertEqual(self.main(self.start("reviewer")), [])
        self.assertEqual(self.main(self.turn()), [])
        # And: the skill typed again begins a new run
        self.assertEqual(self.begun(), [guard.Said("Start `changelog:writer`.")])

    def test_a_start_not_given_back_as_claude_code_gives_it_is_an_error_and_stays_due(self):
        for back in ({"status": "running", "agentId": "w1"}, {"status": LAUNCHED}, "done"):
            with self.subTest(back=back):
                # Given: the run begun, writer due
                # When: writer's start comes back with a status Claude Code gives no start, with
                # no ID, or with no object
                told = self.main(self.start("writer", "PostToolUse", back))
                # Then: it is an error for Claude Code, and writer's start stays due
                self.assertTrue(told[0].error)
                self.assertIn("$.tool_response", told[0].text)
                self.assertEqual(told[1:], [guard.Said(START_WRITER)])

    def test_a_call_of_the_main_conversation_coming_back_in_the_run_tells_nothing(self):
        # Given: the run begun, writer due
        # When: a Bash call of the main conversation comes back
        back = {**self.bash("ls", None, "PostToolUse"), "tool_response": {"stdout": ""}}
        # Then: nothing is told, and nothing is kept
        self.assertEqual(self.main(back), [])
        self.assertEqual(called.calls(helpers.KEPT, called.RUN), [])

    def test_a_start_coming_back_once_the_run_is_over_is_kept_out_of_it(self):
        # Given: the run over, reviewer having given `good`
        self.through("writer", "w1", "written")
        self.through("reviewer", "r1", "good")
        # When: a start of writer comes back
        told = self.main(self.start("writer", "PostToolUse", helpers.back("w2", LAUNCHED)))
        # Then: nothing is told, and it is not kept as a start of the run
        self.assertEqual(told, [])
        self.assertEqual(len(called.starts(helpers.KEPT, called.RUN, ["writer"], "changelog")), 1)


START_WRITER = "Start `changelog:writer`."
AGAIN_WRITER = "writer ended with no result. Start `changelog:writer` again."


class TestTurn(RoutedTest):
    def setUp(self) -> None:
        super().setUp()
        self.begun()

    def test_a_turn_ending_with_a_start_due_is_kept_going_once_then_let_end(self):
        # Given: the run begun, writer due
        # When: the main conversation ends its turn, and, kept going, ends it again
        kept, ended = self.main(self.turn()), self.main(self.turn(True))
        # Then: it is kept going once with the sentence and the start due, then let end, the user
        # told the start left and the step to fix
        self.assertEqual(kept, [guard.Said(helpers.FOLLOW), guard.Said(START_WRITER)])
        left = (
            "lane let the run of write end with `changelog:writer` still due: the maker of"
            " changelog must fix step 1 of write in skills/write/SKILL.md, which starts it."
        )
        self.assertEqual(ended, [guard.Said(left, note=True)])
        # And: the run is over, so a start goes on
        self.assertEqual(self.main(self.start("reviewer")), [])

    def test_a_turn_ending_while_a_start_of_the_run_still_runs_ends(self):
        # Given: writer started, still running
        self.launched("writer", "w1")
        # When: the main conversation ends its turn
        # Then: it ends
        self.assertEqual(self.main(self.turn()), [])

    def test_a_subagent_ended_with_no_result_is_started_again_and_not_resumed(self):
        # Given: writer started, ending with no result once kept going
        self.launched("writer", "w1")
        self.told(guard.started, self.subagent("SubagentStart", "writer", "w1"), "writer")
        for active in (False, True):
            stop = self.subagent("SubagentStop", "writer", "w1", active)
            self.told(guard.stopping, stop, "writer")
        # When: its end reaches the main conversation, which sends it a message, and then
        # starts writer again
        told = self.main(self.notified("w1"))
        message = self.event("SendMessage", {"to": "w1", "message": "Go on."}, None)
        resumed = self.main(message)
        again = self.launched("writer", "w2")
        # Then: it is told to start writer again, the message is stopped with that start, and
        # the start goes through, joined to the first in its place
        self.assertEqual(told, [guard.Said(AGAIN_WRITER)])
        self.assertEqual(resumed, [guard.Said(helpers.FOLLOW), guard.Said(AGAIN_WRITER)])
        self.assertEqual(again, [guard.Said(WAIT_WRITER)])
        joined = [c.get("joined") for c in called.calls(helpers.KEPT, called.RUN)]
        self.assertEqual(joined, [None, "again"])
        # And: a message to it after is stopped with the wait, and so is one to writer's second
        # start, as only the person's answer to a point resumes a start
        stopped = [guard.Said(helpers.FOLLOW), guard.Said(WAIT_WRITER)]
        self.assertEqual(self.main(message), stopped)
        other = self.event("SendMessage", {"to": "w2", "message": "Go on."}, None)
        none = guard.RESUME_NONE.format(named="changelog:writer")
        self.assertEqual(self.main(other), [guard.Said(none), guard.Said(WAIT_WRITER)])

    def test_the_run_let_end_with_a_subagent_due_again_names_its_last_step(self):
        # Given: writer ended with no result, so it is due again
        self.launched("writer", "w1")
        self.told(guard.started, self.subagent("SubagentStart", "writer", "w1"), "writer")
        for active in (False, True):
            self.told(
                guard.stopping, self.subagent("SubagentStop", "writer", "w1", active), "writer"
            )
        # When: the main conversation, kept going once, ends its turn again
        self.main(self.turn())
        ended = self.main(self.turn(True))
        # Then: the user is told to fix writer's last step, which gives its result
        left = (
            "lane let the run of write end with `changelog:writer` still due, as writer ended"
            " with no result: the maker of changelog must fix step 4 of writer in"
            " agents/writer.md, which gives its result."
        )
        self.assertEqual(ended, [guard.Said(left, note=True)])


class TestResumed(RoutedTest):
    """A start resumed with SendMessage after it gave a result, which gives another: the later
    result moves the routes on, as docs/routes.md's How a subagent gives its result says."""

    def setUp(self) -> None:
        super().setUp()
        self.begun()
        self.through("writer", "w1", "written")
        self.told_end = self.through("reviewer", "r1", "good")
        self.message = self.event("SendMessage", {"to": "r1", "message": "Look again."}, None)

    def resumed(self, again: bool) -> list:
        """reviewer, which gave `good`, resumed by the main conversation, started again where
        `again`, giving `more` and ending: what its end tells the main conversation."""
        self.assertEqual(self.main(self.message), [])
        guard.handed("changelog", self.message, "PreToolUse")
        if again:
            start = self.subagent("SubagentStart", "reviewer", "r1")
            self.told(guard.started, start, "reviewer")
        command = f"python3 {self.plugin}/hooks/lane/result.py reviewer more"
        back = self.came_back(command, "changelog:reviewer", "r1")
        self.told(guard.came_back, back, "reviewer")
        self.told(guard.stopping, self.subagent("SubagentStop", "reviewer", "r1"), "reviewer")
        return self.main(self.notified("r1"))

    def test_a_later_result_of_the_resumed_start_moves_the_routes_on(self):
        for again in (True, False):
            with self.subTest(again=again):
                # Given: reviewer gave `good`, so no more starts were told
                self.setUp()
                self.assertEqual(
                    self.told_end, [guard.Said("reviewer gave `good`. Start no more subagents.")]
                )
                # When: reviewer is resumed, started again or not, and gives `more`
                told = self.resumed(again)
                # Then: the main conversation is told to start writer, and its start goes
                # through
                said = guard.Said("reviewer gave `more`. Start `changelog:writer`.")
                self.assertEqual(told, [said])
                self.assertEqual(self.main(self.start("writer")), [])

    def test_while_the_resumed_start_goes_on_the_main_conversation_waits_for_it(self):
        # Given: reviewer, which gave `good`, resumed and started again
        guard.handed("changelog", self.message, "PreToolUse")
        self.told(guard.started, self.subagent("SubagentStart", "reviewer", "r1"), "reviewer")
        # When: the main conversation starts writer meanwhile
        told = self.main(self.start("writer"))
        # Then: it is told to wait for reviewer
        wait = "Wait for `changelog:reviewer` to end: you are told the next start once it has."
        self.assertEqual(told, [guard.Said(helpers.FOLLOW), guard.Said(wait)])


class TestWaits(RoutedTest):
    """A route from reviewer on `asks` that waits for the user, as docs/routes.md's routes give
    `waits`: the run goes on with no start due while the user answers."""

    ASKED = (
        "reviewer gave `asks`. Put its point to the user, and resume `changelog:reviewer` with"
        " their answer by SendMessage."
    )

    def setUp(self) -> None:
        super().setUp()
        routed = {**helpers.ROUTES, "routes": [*helpers.ROUTES["routes"], ASKS]}
        self.write_json(
            os.path.join(self.plugin, "hooks", "lanes.json"), {**helpers.RULES, "routes": routed}
        )
        # Given: the run begun, writer gave `written`, and reviewer gave `asks`
        self.begun()
        self.through("writer", "w1", "written")
        self.told_asks = self.through("reviewer", "r1", "asks")
        answer = {"to": "r1", "message": f"{guard.ANSWER}\nIt is 0.2.0."}
        self.message = self.event("SendMessage", answer, None)

    def test_the_main_conversation_is_told_to_put_the_point_and_resume_with_the_answer(self):
        # When: reviewer's end reaches the main conversation
        # Then: it is told to put reviewer's point to the user and resume it with the answer
        self.assertEqual(self.told_asks, [guard.Said(self.ASKED)])

    def test_the_turn_ends_and_the_run_goes_on_while_the_user_answers(self):
        # When: the main conversation ends its turn to wait for the user's answer
        ended = self.main(self.turn())
        # Then: it ends, and the run goes on: a start meanwhile is stopped with the point to put
        self.assertEqual(ended, [])
        stopped = [guard.Said(helpers.FOLLOW), guard.Said(self.ASKED)]
        self.assertEqual(self.main(self.start("writer")), stopped)
        self.assertEqual(self.main(self.start("reviewer")), stopped)

    def test_a_new_call_of_the_skill_while_the_user_is_to_answer_begins_another_run(self):
        for n, event in enumerate(
            (self.expansion(), self.skill_call("changelog:write", "PostToolUse")), 2
        ):
            with self.subTest(event=event["hook_event_name"]):
                # Given: the run waiting for the user's answer to reviewer's point, the second
                # time a run of its own
                if n > 2:
                    self.through("writer", f"w{n}", "written")
                    self.through("reviewer", f"r{n}", "asks")
                # When: `/changelog:write` is typed, or an AI calls the skill, again
                told = self.main(event)
                # Then: the waiting run ends and another begins: the first start is told, a start
                # of reviewer is stopped with it, and the start of writer goes through
                start = guard.Said("Start `changelog:writer`.")
                self.assertEqual(told, [start])
                stopped = [guard.Said(helpers.FOLLOW), start]
                self.assertEqual(self.main(self.start("reviewer")), stopped)
                self.assertEqual(self.main(self.start("writer")), [])
                # And: a call again before the new run waits begins no other
                self.assertEqual(self.main(event), [])

    def test_the_resumed_subagents_later_result_moves_the_routes_on(self):
        # When: the user answers, the main conversation resumes reviewer with the answer, which
        # Claude Code starts again, and reviewer gives `more` and ends
        self.main(self.prompt("It is 0.2.0."))
        sent = self.main(self.message)
        guard.handed("changelog", self.message, "PreToolUse")
        self.told(guard.started, self.subagent("SubagentStart", "reviewer", "r1"), "reviewer")
        meanwhile = self.main(self.start("writer"))
        command = f"python3 {self.plugin}/hooks/lane/result.py reviewer more"
        self.told(guard.came_back, self.came_back(command, "changelog:reviewer", "r1"), "reviewer")
        self.told(guard.stopping, self.subagent("SubagentStop", "reviewer", "r1"), "reviewer")
        told = self.main(self.notified("r1"))
        # Then: the message goes through, a start while reviewer runs is told to wait, and its
        # end tells the start of writer, which goes through
        self.assertEqual(sent, [])
        wait = "Wait for `changelog:reviewer` to end: you are told the next start once it has."
        self.assertEqual(meanwhile, [guard.Said(helpers.FOLLOW), guard.Said(wait)])
        self.assertEqual(told, [guard.Said("reviewer gave `more`. Start `changelog:writer`.")])
        self.assertEqual(self.main(self.start("writer")), [])


# A route from reviewer that waits for the user, on `asks`, beside docs/routes.md's.
ASKS = {"from": "reviewer", "on": "asks", "waits": True}


class TestUnstepped(RoutedTest):
    """Routes that name no step of the skill, whose part holds no numbered list: the routes'
    sentences are told as the run begins, as no step says them."""

    def setUp(self) -> None:
        super().setUp()
        routed = {k: v for k, v in helpers.ROUTES.items() if k != "step"}
        self.write(self.skill_file, helpers.SKILL)
        laid = {**helpers.RULES, "routes": routed}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def test_the_run_begins_telling_the_routes_sentences_and_the_first_start(self):
        # Given: the routes laid from write with no step, its file saying neither sentence
        # When: `/changelog:write` is typed
        told = self.begun()
        # Then: the routes' sentence, the skill's result command and the first start are told
        ends = helpers.END_WRITE.replace("${CLAUDE_PLUGIN_ROOT}", self.plugin)
        start = "Start `changelog:writer`."
        self.assertEqual(told, [guard.Said(helpers.FOLLOW), guard.Said(ends), guard.Said(start)])

    def test_a_run_let_end_with_a_start_due_names_the_skills_file(self):
        # Given: the run begun, and the main conversation kept going once with writer due
        self.begun()
        self.main(self.turn())
        # When: it ends its turn again
        told = self.main(self.turn(active=True))
        # Then: the user is told to fix the skill's file, which starts it
        said = (
            "lane let the run of write end with `changelog:writer` still due: the maker of"
            " changelog must fix skills/write/SKILL.md, which starts it."
        )
        self.assertEqual(told, [guard.Said(said, note=True)])


# The command the routes name that gives each start its text, and what it prints for writer.
TEXT_COMMAND = "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/start.py"
WRITER_TEXT = '{"work": "CHANGELOG.md"}'


class TestStartText(RoutedTest):
    """Routes naming the command that gives each start its text: a start goes through only with the
    text that the command's last run printed for its subagent."""

    def setUp(self) -> None:
        super().setUp()
        routed = {**helpers.ROUTES, "command": TEXT_COMMAND}
        laid = {**helpers.RULES, "routes": routed}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        self.command = f"python3 {self.plugin}/scripts/start.py"

    def ran_command(self, name: str, printed: str) -> list:
        """The main conversation's run of the command for the subagent of the name come back,
        having printed the text: what it is told."""
        given = {"command": f"{self.command} {name}", "description": "d"}
        back = {"stdout": printed + "\n", "stderr": "", "interrupted": False, "isImage": False}
        event = {**self.event("Bash", given, None, "PostToolUse"), "tool_response": back}
        return self.main(event)

    def started_with(self, name: str, prompt: str) -> list:
        """The main conversation's start of the subagent of the name with the prompt: what its
        PreToolUse is told."""
        event = self.start(name)
        event["tool_input"]["prompt"] = prompt
        return self.main(event)

    def test_the_first_start_is_told_with_the_command_to_run(self):
        # Given: the routes laid with the command
        # When: `/changelog:write` is typed
        told = self.begun()
        # Then: the start is told with the command that gives its text
        said = (
            f"Start `changelog:writer`. Run `{self.command} writer` first, and start it with what"
            " it prints as its prompt, word for word."
        )
        self.assertEqual(told, [guard.Said(said)])

    def test_a_start_with_the_text_the_command_printed_goes_through(self):
        # Given: the run begun, and the command run for writer
        self.begun()
        kept = self.ran_command("writer", WRITER_TEXT)
        # When: writer is started with what it printed
        told = self.started_with("writer", WRITER_TEXT)
        # Then: the run of the command is told nothing, and the start goes through
        self.assertEqual((kept, told), ([], []))

    def test_a_start_with_another_text_or_before_the_command_ran_is_stopped(self):
        for ran in (True, False):
            with self.subTest(ran=ran):
                # Given: the run begun, and the command run for writer or not
                self.setUp()
                self.begun()
                if ran:
                    self.ran_command("writer", WRITER_TEXT)
                # When: writer is started with a prompt of the main conversation's own, or with
                # other values
                told = self.started_with("writer", 'Write the entries. {"work": "CHANGELOG.md"}')
                other = self.started_with("writer", '{"work": "x.md"}')
                # Then: it is stopped with the sentence and the text to start it with
                said = (
                    f"Start `changelog:writer` with what `{self.command} writer` printed as its"
                    " prompt, word for word: run it first where you haven't."
                )
                self.assertEqual(told, [guard.Said(helpers.FOLLOW), guard.Said(said)])
                self.assertEqual(other, told)

    def test_a_point_to_put_or_the_end_is_told_with_no_command_to_run(self):
        # Given: the routes laid with the command, and reviewer's `asks` waiting for the user
        routed = {**helpers.ROUTES, "command": TEXT_COMMAND}
        routed["routes"] = [*routed["routes"], ASKS]
        laid = {**helpers.RULES, "routes": routed}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        for n, on in ((1, "asks"), (2, "good")):
            self.begun()
            self.ran_command("writer", "p")
            self.launched_with("writer", f"w{n}")
            self.ran("writer", f"w{n}", "written")
            self.main(self.notified(f"w{n}"))
            self.ran_command("reviewer", "p")
            self.launched_with("reviewer", f"r{n}")
            self.ran("reviewer", f"r{n}", on)
            told = self.main(self.notified(f"r{n}"))
            # Then: neither the point to put nor the end names the command, as neither is a start
            self.assertEqual(len(told), 1)
            self.assertNotIn("Run `", told[0].text)

    def launched_with(self, name: str, agent_id: str) -> None:
        """The main conversation's start of the subagent with the text "p", launched with the
        ID."""
        self.assertEqual(self.started_with(name, "p"), [])
        back = helpers.back(agent_id, LAUNCHED)
        event = self.start(name, "PostToolUse", back)
        event["tool_input"]["prompt"] = "p"
        self.main(event)

    def test_the_last_run_of_the_command_for_the_subagent_counts(self):
        # Given: the run begun, the command run for writer twice, and once for reviewer
        self.begun()
        self.ran_command("writer", "first")
        self.ran_command("writer", WRITER_TEXT)
        self.ran_command("reviewer", "for reviewer")
        # When: writer is started with the first text, then with the last
        # Then: the first is stopped, and the last goes through
        self.assertNotEqual(self.started_with("writer", "first"), [])
        self.assertEqual(self.started_with("writer", WRITER_TEXT), [])

    def test_a_run_of_the_command_that_gives_no_stdout_is_an_error(self):
        # Given: the run begun
        self.begun()
        given = {"command": f"{self.command} writer", "description": "d"}
        event = {**self.event("Bash", given, None, "PostToolUse"), "tool_response": "x"}
        # When: the command comes back with no stdout
        told = self.main(event)
        # Then: it is an error that Claude Code must fix
        self.assertTrue(told[0].error)
        self.assertIn("$.tool_response: expected an object", told[0].text)


class TestAnswer(RoutedTest):
    """A subagent whose route waits, resumed only with the line of the person's answer and the
    person's own words since its point."""

    def setUp(self) -> None:
        super().setUp()
        routed = {**helpers.ROUTES, "routes": [*helpers.ROUTES["routes"], ASKS]}
        laid = {**helpers.RULES, "routes": routed}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        self.begun()
        self.through("writer", "w1", "written")
        self.through("reviewer", "r1", "asks")

    def resume(self, text: str, to: str = "r1") -> list:
        """The main conversation's SendMessage to the start of the ID with the text: what its
        PreToolUse is told."""
        return self.main(self.event("SendMessage", {"to": to, "message": text}, None))

    def test_the_persons_prompt_is_told_back_as_the_message_to_send(self):
        # Given: reviewer's point put to the user
        # When: the user answers in two prompts
        first = self.main(self.prompt("It is 0.2.0."))
        second = self.main(self.prompt("And keep the date."))
        # Then: each is told the message to resume reviewer with, the person's words so far
        head = "Resume `changelog:reviewer` by SendMessage with this message, word for word:"
        both = f"{guard.ANSWER}\nIt is 0.2.0.\n\nAnd keep the date."
        self.assertEqual(
            first, [guard.Said(head), guard.Said(f"{guard.ANSWER}\nIt is 0.2.0.", plain=True)]
        )
        self.assertEqual(second, [guard.Said(head), guard.Said(both, plain=True)])

    def test_a_resume_with_the_persons_words_alone_goes_through(self):
        # Given: the user answered
        self.main(self.prompt("It is 0.2.0."))
        # When: reviewer is resumed with the line and the answer
        # Then: the message goes through
        self.assertEqual(self.resume(f"{guard.ANSWER}\nIt is 0.2.0."), [])

    def test_a_resume_in_other_words_is_stopped_with_the_message_to_send(self):
        for text in ("The user says 0.2.0.", f"{guard.ANSWER}\nIt is 0.2.0, the user says."):
            with self.subTest(text=text):
                # Given: the user answered
                self.setUp()
                self.main(self.prompt("It is 0.2.0."))
                # When: reviewer is resumed with words of the main conversation's own
                told = self.resume(text)
                # Then: it is stopped with the message it must send
                said = guard.RESUME_ONLY.format(named="changelog:reviewer")
                message = f"{guard.ANSWER}\nIt is 0.2.0."
                self.assertEqual(told, [guard.Said(said), guard.Said(message, plain=True)])

    def test_a_resume_before_the_person_answered_is_stopped(self):
        # Given: reviewer's point put to the user, who has not answered
        # When: reviewer is resumed
        told = self.resume(f"{guard.ANSWER}\nIt is 0.2.0.")
        # Then: it is stopped, the point still to be put
        said = guard.NO_ANSWER.format(named="changelog:reviewer")
        self.assertEqual(told, [guard.Said(said), guard.Said(TestWaits.ASKED)])

    def test_the_words_before_a_resume_are_not_sent_again(self):
        # Given: reviewer resumed with the answer, giving `asks` again
        self.main(self.prompt("It is 0.2.0."))
        self.resume(f"{guard.ANSWER}\nIt is 0.2.0.")
        self.ran("reviewer", "r1", "asks")
        self.main(self.notified("r1"))
        # When: the user answers again
        told = self.main(self.prompt("Yes."))
        # Then: only the new answer is told as the message
        self.assertEqual(told[1], guard.Said(f"{guard.ANSWER}\nYes.", plain=True))

    def test_a_resume_of_a_start_whose_point_is_not_put_is_stopped(self):
        # Given: the user answered reviewer's point
        self.main(self.prompt("It is 0.2.0."))
        # When: writer, whose start gave `written`, is resumed
        told = self.resume("Write again.", "w1")
        # Then: it is stopped, as only a point's answer resumes a start
        said = guard.RESUME_NONE.format(named="changelog:writer")
        self.assertEqual(told, [guard.Said(said), guard.Said(TestWaits.ASKED)])

    def test_the_skills_command_typed_or_a_notification_is_no_answer(self):
        for text in ("/changelog:write again", " <task-notification>x</task-notification>"):
            with self.subTest(text=text):
                # Given: reviewer's point put to the user
                self.setUp()
                # When: the user types the skill's command, or a notification is handed in
                told = self.main(self.prompt(text))
                # Then: the point is told still, and no answer is kept
                self.assertEqual(told, [guard.Said(TestWaits.ASKED)])
                said = guard.NO_ANSWER.format(named="changelog:reviewer")
                answer = self.resume(f"{guard.ANSWER}\n{text}")
                self.assertEqual(answer, [guard.Said(said), guard.Said(TestWaits.ASKED)])

    def test_a_message_to_no_start_of_the_run_goes_through(self):
        # Given: reviewer's point put to the user
        # When: the main conversation sends a message to a run that is no start of the run
        # Then: it goes through
        self.assertEqual(self.resume("Hello.", "x9"), [])


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

    def test_examiner_is_started_after_written_and_its_result_leads_on(self):
        # Given: the run begun, and writer gave `written`
        self.begun()
        told = self.through("writer", "w1", "written")
        # When: examiner is started, gives `asks` by checker's script, and ends
        start = self.launched("checker:examiner", "e1")
        name = "checker:examiner"
        self.told(guard.started, self.subagent("SubagentStart", name, "e1"), name)
        back = self.came_back(self.examined("asks"), name, "e1")
        self.assertEqual(self.told(guard.came_back, back, name), [])
        self.assertEqual(
            self.told(guard.stopping, self.subagent("SubagentStop", name, "e1"), name), []
        )
        # Then: examiner is told by its type, its start goes through, its result is kept in
        # changelog's record, and its end tells to put its point to the user, as the route on
        # `asks` waits
        self.assertEqual(told, [guard.Said("writer gave `written`. Start `checker:examiner`.")])
        wait = "Wait for `checker:examiner` to end: you are told the next start once it has."
        self.assertEqual(start, [guard.Said(wait)])
        self.assertEqual(called.result(helpers.KEPT, "e1"), "asks")
        asked = (
            "checker:examiner gave `asks`. Put its point to the user, and resume"
            " `checker:examiner` with their answer by SendMessage."
        )
        self.assertEqual(self.main(self.notified("e1")), [guard.Said(asked)])

    def test_examiner_is_told_nothing_as_it_starts(self):
        # Given: examiner, whose own plugin's guard tells it its sentences
        name = "checker:examiner"
        # When: it starts
        told = self.told(guard.started, self.subagent("SubagentStart", name, "e1"), name)
        # Then: changelog's guard tells it nothing
        self.assertEqual(told, [])

    def test_writer_is_stopped_starting_examiner(self):
        # Given: writer, and routes that name examiner, a dependency's subagent
        given = {"prompt": "p", "subagent_type": "checker:examiner"}
        # When: writer starts it
        told = self.told(guard.check, self.event("Agent", given), "writer")
        # Then: it is stopped, as the main conversation alone starts one
        self.assertEqual(told, [guard.Said(guard.MAIN_STARTS)])

    def test_examiners_calls_are_left_to_its_own_plugins_guard(self):
        # Given: examiner, whose calls changelog lays no lane on
        event = self.event("Bash", {"command": "rm -r ."}, "checker:examiner", agent_id="e1")
        # When: it runs a command
        # Then: changelog's guard tells it nothing
        self.assertEqual(self.told(guard.check, event, "checker:examiner"), [])

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
            f"End by running `{helpers.EXAMINED} asks` or `{helpers.EXAMINED} done`."
            f"{helpers.NOT_WORK}\n"
            "Each `${dependency:<name>}` is the folder the plugin of the name is installed in, as"
            " its skill gives the command."
        )
        self.assertEqual(first, [guard.Said(said)])
        self.assertEqual(again, [])
        self.assertTrue(called.ended(helpers.KEPT, "e1"))

    def test_the_run_let_end_with_examiner_due_again_tells_whose_fix_it_is(self):
        # Given: examiner started in the run, ending with no result, kept going once
        self.begun()
        self.through("writer", "w1", "written")
        name = "checker:examiner"
        self.launched(name, "e1")
        self.told(guard.started, self.subagent("SubagentStart", name, "e1"), name)
        for active in (False, True):
            self.told(guard.stopping, self.subagent("SubagentStop", name, "e1", active), name)
        # When: the main conversation, kept going once with examiner due again, ends its turn
        # again
        self.main(self.turn())
        ended = self.main(self.turn(True))
        # Then: the user is told the maker of checker or of changelog must fix it
        said = (
            "lane let the run of write end with `checker:examiner` still due, as checker:examiner"
            " ended with no result the routes take: the maker of checker must have examiner give"
            " `asks` or `done`, or the maker of changelog must route the result it gives."
        )
        self.assertEqual(ended, [guard.Said(said, note=True)])

    def test_another_plugins_subagent_is_left_alone_where_lanes_json_cannot_be_read(self):
        # Given: hooks/lanes.json removed
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        # When: examiner is about to end
        event = self.subagent("SubagentStop", "checker:examiner", "e1")
        # Then: changelog's guard tells it nothing, as whether the routes name it cannot be read
        self.assertEqual(self.told(guard.stopping, event, "checker:examiner"), [])

    def test_a_dependencys_subagent_the_routes_do_not_name_is_left_alone(self):
        # Given: checker's linter, which the routes do not name
        event = self.subagent("SubagentStop", "checker:linter", "x1")
        # When: it is about to end
        # Then: changelog's guard tells it nothing and keeps nothing
        self.assertEqual(self.told(guard.stopping, event, "checker:linter"), [])
        self.assertEqual(called.kept(helpers.KEPT, "x1"), [])


# Routes from writer to checker's skill check, which gives `done` by checker's result script in the
# main conversation, ending the run.
SKILL_ROUTES = {
    "orchestrator": "write",
    "step": 1,
    "routes": [
        {"from": "write", "to": "writer"},
        {"from": "writer", "on": "written", "to": "checker:check"},
        {"from": "checker:check", "on": "done", "to": "reviewer"},
        {"from": "reviewer", "on": "good"},
    ],
}


class TestDependencysSkill(RoutedTest):
    """A dependency's skill the routes name, checker's check: one move, begun by its Skill call and
    ended by the run of checker's result script in the main conversation, changelog's guard
    checking nothing meanwhile."""

    def setUp(self) -> None:
        super().setUp()
        self.depend()
        laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
        self.write_json(
            os.path.join(self.plugin, "hooks", "lanes.json"), {**laid, "routes": SKILL_ROUTES}
        )
        self.folder = os.path.join(self.base, "checker")
        self.begun()
        self.told_due = self.through("writer", "w1", "written")

    def checked(self, on: str) -> dict:
        """The main conversation's run of checker's result script giving the result for check,
        come back."""
        command = f"python3 {self.folder}/hooks/lane/result.py check {on}"
        return {**self.bash(command, None, "PostToolUse"), "tool_response": {"stdout": ""}}

    def test_writer_is_stopped_calling_check(self):
        # Given: writer, and routes that name check, a dependency's skill
        # When: writer calls it
        told = self.told(guard.check, self.event("Skill", {"skill": "checker:check"}), "writer")
        # Then: it is stopped, as the main conversation alone starts one
        self.assertEqual(told, [guard.Said(guard.MAIN_STARTS)])

    def test_the_skill_due_is_called_and_its_result_leads_on(self):
        # Given: writer gave `written`, so check is due
        # When: the main conversation calls check, which starts a subagent of checker's, ends its
        # turn and is prompted meanwhile, then runs checker's result script giving `done`
        call = self.main(self.skill_call("checker:check"))
        begun = self.main(self.skill_call("checker:check", "PostToolUse"))
        meanwhile = [
            self.main(self.start("checker:examiner")),
            self.main(self.start("reviewer")),
            self.main(self.turn()),
            self.main(self.prompt()),
            self.main({**self.bash("ls", None, "PostToolUse"), "tool_response": {}}),
            self.main(
                {**self.event("Read", {"file_path": "a"}, None, "PostToolUse"), "tool_response": {}}
            ),
        ]
        done = self.main(self.checked("done"))
        # Then: check is told as due, its call goes through, nothing is told meanwhile, and its
        # result tells the next start
        self.assertEqual(
            self.told_due, [guard.Said("writer gave `written`. Start `checker:check`.")]
        )
        self.assertEqual((call, begun), ([], []))
        self.assertEqual(meanwhile, [[], [], [], [], [], []])
        self.assertEqual(
            done, [guard.Said("checker:check gave `done`. Start `changelog:reviewer`.")]
        )
        # And: the start of reviewer goes through
        self.assertEqual(self.main(self.start("reviewer")), [])

    def test_the_skill_not_due_is_stopped_with_the_start_due(self):
        # Given: check due
        # When: the main conversation starts reviewer, or, with check given, calls check again
        stopped = self.main(self.start("reviewer"))
        # Then: it is stopped with the start due
        due = "writer gave `written`. Start `checker:check`."
        self.assertEqual(stopped, [guard.Said(helpers.FOLLOW), guard.Said(due)])

    def test_a_result_no_route_from_the_skill_is_on_ends_no_move(self):
        # Given: check called
        self.main(self.skill_call("checker:check", "PostToolUse"))
        # When: checker's result script comes back giving `asks`
        # Then: nothing is told, and the move goes on
        self.assertEqual(self.main(self.checked("asks")), [])
        self.assertEqual(self.main(self.start("reviewer")), [])

    def test_a_skill_call_with_no_id_is_an_error(self):
        # Given: check due
        # When: its call comes back with no tool_use_id
        event = self.skill_call("checker:check", "PostToolUse")
        del event["tool_use_id"]
        told = self.main(event)
        # Then: it is an error for Claude Code
        self.assertTrue(told[0].error)
        self.assertIn("$.tool_use_id", told[0].text)


class TestFanOut(RoutedTest):
    """reviewer fanned out, its results taken in the order `more`, `good`."""

    WAIT = (
        "Wait for every run of `changelog:reviewer` to end: you are told the next start once each"
        " has."
    )

    def setUp(self) -> None:
        super().setUp()
        self.fan_out(["more", "good"])
        # Given: the run begun, and writer gave `written`, so reviewer is due
        self.begun()
        self.through("writer", "w1", "written")

    def fan_out(self, precedence: object) -> None:
        """Lays the routes with reviewer fanned out, its results in the order given, or none."""
        routed = {**helpers.ROUTES, "fan_out": ["reviewer"]}
        routed.update({"precedence": precedence} if precedence else {})
        laid = {**helpers.RULES, "routes": routed}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def test_several_starts_go_through_and_the_next_is_told_once_every_one_has_ended(self):
        # When: the main conversation starts reviewer twice
        # Then: both go through, each told to wait for every start
        self.assertEqual(self.launched("reviewer", "r1"), [guard.Said(self.WAIT)])
        self.assertEqual(self.launched("reviewer", "r2"), [guard.Said(self.WAIT)])
        # And: the second is kept joined to the first
        joined = [c.get("joined") for c in called.calls(helpers.KEPT, called.RUN)]
        self.assertEqual(joined, [None, None, "more"])
        # And: writer's start is stopped while either runs, and once the first gives `more`
        stopped = [guard.Said(helpers.FOLLOW), guard.Said(self.WAIT)]
        self.assertEqual(self.main(self.start("writer")), stopped)
        self.ran("reviewer", "r1", "more")
        self.assertEqual(self.main(self.notified("r1")), [guard.Said(self.WAIT)])
        self.assertEqual(self.main(self.start("writer")), stopped)
        # And: once the second ends with `good`, writer is told, by the order of the results
        self.ran("reviewer", "r2", "good")
        told = [guard.Said("The 2 runs of reviewer gave `more`. Start `changelog:writer`.")]
        self.assertEqual(self.main(self.notified("r2")), told)
        self.assertEqual(self.main(self.start("writer")), [])

    def test_a_start_ending_with_no_result_has_reviewer_started_again_into_the_starts(self):
        # Given: two starts of reviewer, the first giving `good`, the second ending with no
        # result after it was kept going once
        self.launched("reviewer", "r1")
        self.launched("reviewer", "r2")
        self.ran("reviewer", "r1", "good")
        self.told(guard.started, self.subagent("SubagentStart", "reviewer", "r2"), "reviewer")
        for active in (False, True):
            stop = self.subagent("SubagentStop", "reviewer", "r2", active=active)
            self.told(guard.stopping, stop, "reviewer")
        # When: its end reaches the main conversation
        # Then: it is told to start reviewer again
        again = "reviewer ended with no result. Start `changelog:reviewer` again."
        self.assertEqual(self.main(self.notified("r2")), [guard.Said(again)])
        # And: the start made again gives `more`, which is taken with the first's `good`
        self.launched("reviewer", "r3")
        self.ran("reviewer", "r3", "more")
        told = [guard.Said("The 2 runs of reviewer gave `more`. Start `changelog:writer`.")]
        self.assertEqual(self.main(self.notified("r3")), told)

    def test_results_that_differ_the_routes_laid_again_do_not_order_are_an_error(self):
        # Given: two starts of reviewer at once, giving `more` and `good`
        self.launched("reviewer", "r1")
        self.launched("reviewer", "r2")
        self.ran("reviewer", "r1", "more")
        self.ran("reviewer", "r2", "good")
        # When: the routes are laid again with reviewer no longer fanned out nor its results
        # ordered, before the end reaches the main conversation
        laid = {**helpers.RULES, "routes": helpers.ROUTES}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        # Then: the main conversation is told the error, with who must fix it
        self.assertEqual(
            self.main(self.notified("r2")),
            [
                guard.Said(
                    "lane cannot check the routes of write: the runs of reviewer at once gave"
                    " `more` and `good`, and the routes order not each of them in `precedence`."
                    " Tell the user: the maker of changelog must order the results of reviewer in"
                    " the `precedence` of its routes, and lay them again with `lay.py write`.",
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
                # Given: starts of reviewer that more may join, reviewer due again, or due anew
                # When: a start of reviewer, or of a subagent named before or after it, comes back
                # Then: only reviewer's joins, as a further start or one made again
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

    def test_a_subagent_with_no_run_only_lane_runs_any_command_but_a_result_it_may_not_give(self):
        # Given: reviewer, with no lane but its result commands
        gives = f"python3 {self.plugin}/hooks/lane/result.py reviewer"

        # When: it runs git log --oneline, its result command on `good`, and on `done`
        def run(command: str) -> list:
            return self.told(guard.check, self.bash(command, "changelog:reviewer"), "reviewer")

        # Then: the first two go through, and the third is told the sentence of its last step
        # and the commands it may give a result by
        self.assertEqual(run("git log --oneline"), [])
        self.assertEqual(run(f"{gives} good"), [])
        said = (
            f"End by running `{gives} more` or `{gives} good`.{helpers.NOT_WORK}\n"
            f"The commands you may run, each word for word: `{gives} more`, `{gives} good`."
        )
        self.assertEqual(run(f"{gives} done"), [guard.Said(said)])

    def test_a_subagent_ending_with_no_result_is_kept_going_once_with_its_last_steps_sentence(self):
        # Given: writer started, giving no result
        self.told(guard.started, self.subagent("SubagentStart", "writer", "a1"), "writer")
        # When: it is about to end, and again once kept going
        first = self.told(guard.stopping, self.subagent("SubagentStop", "writer", "a1"), "writer")
        again = self.subagent("SubagentStop", "writer", "a1", active=True)
        # Then: it is told the sentence of its last step, as it reads it, and then ends
        said = f"End by running `{self.writer_gives}`.{helpers.NOT_WORK}"
        self.assertEqual(first, [guard.Said(said)])
        self.assertEqual(self.told(guard.stopping, again, "writer"), [])
        self.assertTrue(called.ended(helpers.KEPT, "a1"))

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
        # Given: writer's last step no longer saying its result sentence
        self.write(self.agent_file, helpers.LAID)
        # When: it makes a call its lanes judge
        told = self.told(guard.check, self.bash("git log --oneline"), "writer")
        # Then: it is an error of the result on its step
        self.assertEqual(len(told), 1)
        self.assertTrue(told[0].error)
        self.assertIn("lane cannot check result on step 4 of writer: step", told[0].text)

    def test_the_skills_step_no_longer_saying_the_routes_sentence_begins_no_run(self):
        # Given: write's step 1 no longer saying the routes' sentence
        self.write(self.skill_file, helpers.SKILL)
        # When: `/changelog:write` is typed
        told = self.begun()
        # Then: it is an error of follow_routes on its step, and no run begins
        self.assertEqual(len(told), 1)
        self.assertTrue(told[0].error)
        self.assertIn("lane cannot check follow_routes on step 1 of write: step 1", told[0].text)
        self.assertFalse(called.begun(helpers.KEPT))

    def test_routes_laid_that_lay_py_print_would_refuse_are_an_error_at_each_event(self):
        # Given: the run begun, then the laid routes fanning out reviewer with no order of its
        # results, as no `lay.py print` lets through
        self.begun()
        laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
        laid["routes"] = {**laid["routes"], "fan_out": ["reviewer"]}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        why = (
            "hooks/lanes.json gives reviewer in `fan_out`, whose results `more` and `good` the"
            " routes do not order in `precedence`, so the result of its runs at once could not be"
            " told. "
        )
        for told, on, then in (
            (self.main(self.start("writer")), "the routes of write", LAY_AGAIN_MAIN),
            (
                self.told(
                    guard.started, self.subagent("SubagentStart", "reviewer", "r1"), "reviewer"
                ),
                "the lanes of reviewer",
                LAY_AGAIN,
            ),
        ):
            with self.subTest(on=on):
                # When: the main conversation starts writer, or reviewer starts
                # Then: it is an error of the laid file, the maker told to lay the routes again
                self.assertEqual(told, [guard.Said(f"lane cannot check {on}: {why}{then}", True)])

    def test_routes_refused_outside_a_run_leave_the_main_conversation_alone(self):
        # Given: the laid routes fanning out reviewer with no order of its results, and no run
        laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
        laid["routes"] = {**laid["routes"], "fan_out": ["reviewer"]}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        # When: the main conversation starts writer
        # Then: nothing is told
        self.assertEqual(self.main(self.start("writer")), [])

    def test_lanes_json_that_cannot_be_read_is_an_error_only_within_a_run(self):
        # Given: hooks/lanes.json removed, before a run and then within one
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        before = self.main(self.start("writer"))
        called.keep(helpers.KEPT, called.RUN, called.START)
        within = self.main(self.start("writer"))
        # Then: nothing is told before, and an error within
        self.assertEqual(before, [])
        said = (
            "lane cannot check the routes of the run: hooks/lanes.json is not there. "
            + LAY_AGAIN_MAIN
        )
        self.assertEqual(within, [guard.Said(said, True)])

    def test_a_starts_kept_calls_that_cannot_be_read_are_an_error(self):
        # Given: the run begun, its start w1 of writer then holding a line that is no entry
        self.begun()
        self.launched("writer", "w1")
        (folder,) = os.listdir(os.path.join(self.base, "lane"))
        with open(os.path.join(self.base, "lane", folder, "w1.jsonl"), "a") as f:
            f.write("x\n")
        # When: the main conversation ends its turn
        told = self.main(self.turn())
        # Then: it is an error, telling it be reported
        self.assertTrue(told[0].error)
        self.assertIn("lane cannot check the routes of write: ", told[0].text)
        self.assertIn("https://github.com/lovaizu/ccpm/issues", told[0].text)

    def test_kept_calls_that_cannot_be_read_are_an_error(self):
        # Given: the run begun, its record then holding a line that is no entry
        self.begun()
        (folder,) = os.listdir(os.path.join(self.base, "lane"))
        with open(os.path.join(self.base, "lane", folder, "run.jsonl"), "a") as f:
            f.write("x\n")
        # When: the main conversation starts writer
        told = self.main(self.start("writer"))
        # Then: it is an error, telling it be reported
        self.assertTrue(told[0].error)
        self.assertIn("lane cannot check the routes of write: ", told[0].text)
        self.assertIn("https://github.com/lovaizu/ccpm/issues", told[0].text)

    def test_an_event_not_as_claude_code_hands_it_is_an_error_only_within_a_run(self):
        # Given: an event the hook found wrong, before a run and within one
        before = self.main(self.start("writer"), "$.cwd: x")
        self.begun()
        within = self.main(self.start("writer"), "$.cwd: x")
        # Then: nothing is told before, and an error for Claude Code within
        self.assertEqual(before, [])
        self.assertTrue(within[0].error)
        self.assertIn("`claude update`", within[0].text)

    def test_a_subagents_event_not_as_claude_code_hands_it_is_an_error_at_every_event(self):
        for check in (guard.came_back, guard.started, guard.stopping):
            with self.subTest(check=check):
                # Given: an event of writer the hook found wrong
                # When: the guard is given it
                said = check(self.plugin, "changelog", "writer", self.bash("ls"), "$.cwd: x")
                # Then: it is an error for Claude Code
                self.assertTrue(said[0].error)
                self.assertIn("`claude update`", said[0].text)

    def test_a_subagent_neither_laid_nor_routed_is_not_checked_at_any_event(self):
        for check in (guard.came_back, guard.started, guard.stopping):
            with self.subTest(check=check):
                # Given: the routes laid, naming no planner
                # When: planner's event reaches the guard
                # Then: nothing is said
                self.assertEqual(
                    self.told(check, self.subagent("SubagentStart", "planner", "p1"), "planner"), []
                )

    def test_a_routed_subagent_whose_file_has_no_step_is_told_its_result_as_it_starts(self):
        # Given: reviewer, with no lane but its result commands, its file holding no step
        reviewer = os.path.join(self.plugin, "agents", "reviewer.md")
        self.write(
            reviewer, "---\nname: reviewer\ndescription: d\nbackground: true\n---\n\nReview.\n"
        )
        # When: it starts, and runs a command
        start = self.subagent("SubagentStart", "reviewer", "a1")
        started = self.told(guard.started, start, "reviewer")
        told = self.told(guard.check, self.bash("ls", "changelog:reviewer"), "reviewer")
        # Then: it is told the sentence of its result as it starts, as no step says it, and its
        # command goes through
        said = helpers.END_REVIEWER.replace("${CLAUDE_PLUGIN_ROOT}", self.plugin)
        self.assertEqual((started, told), ([guard.Said(said)], []))


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
        part = os.path.join(self.plugin, "domain", "writer.md")
        self.write(part, self.read(self.agent_file).split("---\n\n", 1)[1])
        self.write(self.agent_file, helpers.PART_ENTRY.format(name="writer"))
        # When: it reads its part, which it was given whole as it started, or another part
        self.write(os.path.join(self.plugin, "domain", "other.md"), "x\n")
        # Then: its own goes through, and the other is told the sentence
        self.assertEqual(self.check(self.reading(part)), [])
        said = [guard.Said("Read only `CHANGELOG.md` or `docs/`.")]
        other = os.path.join(self.plugin, "domain", "other.md")
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


class TestEditOnly(LanesTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay_lanes([lane("edit_only", "design-tree.md")])
        self.sentence = "Once `design-tree.md` is made, change it only with Edit."

    def test_a_write_of_the_output_once_it_is_there_is_told_the_sentence(self):
        for there, tool, through in (
            (False, "Write", True),
            (True, "Edit", True),
            (True, "Write", False),
            (True, "NotebookEdit", False),
        ):
            with self.subTest(there=there, tool=tool):
                # Given: writer, whose step 3 changes design-tree.md only with Edit once it is
                # made, the file there or not
                path = os.path.join(self.base, "design-tree.md")
                if there:
                    self.write(path, "# Design tree\n")
                elif os.path.exists(path):
                    os.remove(path)
                # When: it writes it with the tool
                told = self.check(self.written("design-tree.md", tool))
                # Then: a Write making it and an Edit go through, and the rest is told the sentence
                self.assertEqual(told, [] if through else [guard.Said(self.sentence)])

    def test_a_command_writing_the_output_is_stopped_only_by_a_run_only_lane(self):
        # Given: writer with edit_only alone, design-tree.md there
        self.write("design-tree.md", "# Design tree\n")
        # When: it runs a command that writes design-tree.md
        told = self.check(self.bash("sed -i s/a/b/ design-tree.md"))
        # Then: it goes through, as edit_only judges Write and Edit alone, and only a run_only
        # lane holds the commands
        self.assertEqual(told, [])


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
        said = f"End by running `{self.gives} asks` or `{self.gives} done`.{helpers.NOT_WORK}"
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
        # When: it gives its result having read nothing, then once it read CHANGELOG.md, having
        # changed src/ untested and answered nothing
        self.ran(helpers.kept_call("Write", file_path="src/a.py", content="x"))
        first = self.check(self.bash(self.done))
        self.write("CHANGELOG.md", "# Changelog\n")
        self.ran(helpers.kept_call("Read", file_path="CHANGELOG.md"))
        told = self.check(self.bash(self.done))
        # Then: step 1 is told first, its trace not come back, and then each lane of the end, with
        # what is missing on the next line
        step_1 = (
            "Read `CHANGELOG.md` to learn its last version and its form. Read `CHANGELOG.md` to its"
            " end.\n`CHANGELOG.md` unread from line 1"
        )
        self.assertEqual([t.text for t in first], [step_1])
        self.assertEqual(
            [t.text for t in told],
            [
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
                self.given("{}")
                # When: writer gives its result having answered nothing
                told = self.check(self.bash(self.done))
                # Then: F1 is unanswered, or the adapter's failure is an error naming it
                if error:
                    self.assertTrue(told[0].error)
                    self.assertIn("the adapter hooks/adapters/items-f.py exited 2", told[0].text)
                    self.assertIn("must fix its adapter hooks/adapters/items-f.py", told[0].text)
                else:
                    self.assertIn("F1 of `review.md` unanswered", told[0].text)

    def test_the_items_adapter_is_given_the_starts_values(self):
        # Given: every_item reading review.md by an adapter that prints what it was given, and
        # writer started with `{"tree": "t.json"}`
        self.write("review.md", "## Finding 1\n")
        adapter = (
            "import json, sys\nprint(json.dumps({'items': [json.dumps(json.load(sys.stdin))]}))\n"
        )
        self.write(os.path.join(self.plugin, "hooks", "adapters", "items-f.py"), adapter)
        self.lay_lanes(
            [lane("every_item", "review.md", number=4, adapter="hooks/adapters/items-f.py")]
        )
        self.given('{"tree": "t.json"}')
        # When: writer gives its result having answered nothing
        told = self.check(self.bash(self.done))
        # Then: the adapter was given the input, its text and the start's values
        given = {"input": "review.md", "text": "## Finding 1\n", "values": {"tree": ["t.json"]}}
        self.assertIn(json.dumps(given), told[0].text)

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
        # Then: its own is put to the person, and the other goes through, as no run_only lane
        # holds writer
        said = "Run `git push origin {branch}` only with the person's approval."
        self.assertEqual(
            self.check(self.bash("git push origin work")), [guard.Said(said, ask=True)]
        )
        self.assertEqual(self.check(self.bash("git push origin main")), [])
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


# writer's step 1 and step 2 as they read with read_whole and run_step laid on them.
STEP_1 = (
    "Read `CHANGELOG.md` to learn its last version and its form. Read `CHANGELOG.md` to its end."
)
STEP_2 = "Read the commits since then with `git log --oneline`. Run `git log --oneline`."


class TestOrder(LanesTest):
    """Steps of the trace kind, read_whole on step 1, run_step on step 2 and write_step on step 3:
    a later step's trace is stopped while an earlier one's hasn't come back, and so is the end
    while any hasn't."""

    def setUp(self) -> None:
        super().setUp()
        self.write("CHANGELOG.md", "# Changelog\n\n## 0.1.0\n")
        self.lay_lanes(
            [
                lane("read_whole", "CHANGELOG.md", number=1),
                lane("run_step", "git log --oneline", number=2),
                lane("write_step", "CHANGELOG.md", number=3),
            ]
        )
        self.done = DONE.format(root=self.plugin)

    def came(self, tool: str, **given: str) -> None:
        """writer's call of the tool with the input, come back."""
        called.keep(helpers.KEPT, "a1", called.call(tool, given))

    def test_a_later_steps_trace_before_an_earlier_ones_is_stopped_with_the_step_due(self):
        for event in (self.bash("git log --oneline"), self.written("CHANGELOG.md")):
            with self.subTest(event=event["tool_name"]):
                # Given: writer, which has read nothing
                # When: it runs step 2's command, or writes step 3's output
                told = self.check(event)
                # Then: it is stopped with step 1, due, and what of it is missing
                said = f"{STEP_1}\n`CHANGELOG.md` unread from line 1"
                self.assertEqual(told, [guard.Said(said)])

    def test_the_due_steps_own_trace_and_a_call_of_no_step_go_through(self):
        for event in (self.reading("CHANGELOG.md"), self.bash("ls"), self.reading("x.md")):
            with self.subTest(event=event["tool_input"]):
                # Given: writer, which has read nothing
                # When: it reads CHANGELOG.md, step 1's trace, or makes a call no step names
                # Then: the call goes through
                self.assertEqual(self.check(event), [])

    def test_once_a_trace_came_back_the_next_step_is_due(self):
        # Given: writer read CHANGELOG.md whole
        self.came("Read", file_path="CHANGELOG.md")
        # When: it runs step 2's command, then writes step 3's output before it
        ran, wrote = (
            self.check(self.bash("git log --oneline")),
            self.check(self.written("CHANGELOG.md")),
        )
        # Then: the command goes through, and the write is stopped with step 2
        self.assertEqual(ran, [])
        self.assertEqual(wrote, [guard.Said(f"{STEP_2}\n`git log --oneline` not run")])

    def test_the_end_with_a_step_not_done_is_stopped_with_the_first(self):
        # Given: writer read CHANGELOG.md whole and wrote it, but never ran step 2's command
        self.came("Read", file_path="CHANGELOG.md")
        self.came("Write", file_path="CHANGELOG.md", content="x")
        # When: it gives its result
        told = self.check(self.bash(self.done))
        # Then: it is stopped with step 2, the first not done
        self.assertEqual(told, [guard.Said(f"{STEP_2}\n`git log --oneline` not run")])

    def test_the_end_with_every_step_done_goes_through(self):
        # Given: writer took each step in order
        self.came("Read", file_path="CHANGELOG.md")
        self.came("Bash", command="git log --oneline")
        self.came("Write", file_path="CHANGELOG.md", content="x")
        # When: it gives its result
        # Then: it goes through
        self.assertEqual(self.check(self.bash(self.done)), [])


class TestPortSteps(LanesTest):
    """Step lists read through a steps adapter, given the start's values: each list held in its
    order, two lists in none between them."""

    def setUp(self) -> None:
        super().setUp()
        adapter = os.path.join(self.plugin, "hooks", "adapters", "steps-w.py")
        self.write(adapter, helpers.STEPS_ADAPTER)
        self.lay_lanes([])
        laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
        laid["subagents"][0]["steps_adapter"] = "hooks/adapters/steps-w.py"
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        self.given('{"intents": ["Q1", "Q2"]}')

    def test_a_later_step_of_a_list_is_stopped_and_another_lists_first_goes_through(self):
        # Given: writer, which has run nothing
        # When: it runs `b`, Q1's second, and `c`, Q2's first
        # Then: `b` is stopped with Q1's first, and `c` goes through
        self.assertEqual(self.check(self.bash("b")), [guard.Said("Run a. Run `a`.\n`a` not run")])
        self.assertEqual(self.check(self.bash("c")), [])

    def test_the_steps_are_told_as_the_subagent_starts(self):
        # Given: writer's start, its prompt kept
        # When: it starts
        told = guard.started(
            self.plugin, "changelog", "writer", self.subagent("SubagentStart", "writer", "a1"), ""
        )
        # Then: it is told each list, in order
        said = (
            f"{guard.STEPS_TOLD}\n\n1. Run a. Run `a`.\n2. Run b. Run `b`."
            "\n\n1. Run c. Run `c`.\n2. Run d. Run `d`."
        )
        self.assertEqual(told, [guard.Said(said)])

    def test_an_adapter_that_fails_or_gives_a_lane_lay_py_refuses_is_an_error(self):
        dependency = helpers.STEPS_ADAPTER.replace(
            '["Run a.", "a"]', '["Run a.", "${dependency:x}/a"]'
        )
        for text, said in (
            ("import sys\nsys.exit(2)\n", "the adapter hooks/adapters/steps-w.py exited 2"),
            (dependency, "the adapter hooks/adapters/steps-w.py gives run_step `${dependency:x}`"),
        ):
            with self.subTest(said=said):
                # Given: the adapter failing, or giving a command of a dependency not declared
                self.write(os.path.join(self.plugin, "hooks", "adapters", "steps-w.py"), text)
                # When: writer runs a command
                told = self.check(self.bash("b"))
                # Then: it is an error naming the adapter, which its maker must fix
                self.assertTrue(told[0].error)
                self.assertIn(f"lane cannot check the steps of writer: {said}", told[0].text)
                self.assertIn("must fix its adapter hooks/adapters/steps-w.py", told[0].text)

    def test_steps_whose_values_cannot_be_read_are_an_error(self):
        for values, said in ((None, "gave back no ID"), ("hooks/adapters/values-w.py", "exited 3")):
            with self.subTest(said=said):
                # Given: writer's start not come back with its prompt, or its values adapter failing
                self.setUp()
                if values is None:
                    os.remove(called.file(helpers.KEPT, "a1", False))
                else:
                    self.write(os.path.join(self.plugin, values), "import sys\nsys.exit(3)\n")
                    laid = self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))
                    laid["subagents"][0]["adapter"] = values
                    self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
                # When: writer runs a command
                with mock.patch.object(guard, "WAIT", 0.0):
                    told = self.check(self.bash("b"))
                # Then: it is an error of its steps
                self.assertTrue(told[0].error)
                self.assertIn("lane cannot check the steps of writer:", told[0].text)
                self.assertIn(said, told[0].text)

    def test_the_steps_are_not_told_as_it_starts_before_its_prompt_is_kept(self):
        # Given: writer's start, its prompt not kept yet
        os.remove(called.file(helpers.KEPT, "a1", False))
        # When: it starts
        start = self.subagent("SubagentStart", "writer", "a1")
        # Then: it is told nothing, as its steps are read given the start's values
        self.assertEqual(guard.started(self.plugin, "changelog", "writer", start, ""), [])

    def test_an_adapter_giving_a_lane_out_of_its_port_is_an_error(self):
        # Given: the adapter giving a lane not of the trace kind
        bad = helpers.STEPS_ADAPTER.replace('"lane": "run_step"', '"lane": "run_only"')
        self.write(os.path.join(self.plugin, "hooks", "adapters", "steps-w.py"), bad)
        # When: writer runs a command
        told = self.check(self.bash("b"))
        # Then: it is an error naming the adapter
        self.assertTrue(told[0].error)
        self.assertIn(
            "the adapter hooks/adapters/steps-w.py answered out of the steps port", told[0].text
        )


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
        self.part = os.path.join(self.plugin, "domain", "writer.md")
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
            "lane cannot check the lanes of writer: its part domain/writer.md is not there",
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
