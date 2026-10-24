"""The guard: in the subagent its command names, and there alone, a call that drifts from a lane is
stopped and the subagent told `<plugin>: <sentence>`; a lane whose step no longer says its sentence
stops the call and says to have lane:up run again."""

import contextlib
import io
import json
import os
import runpy
import sys
from unittest import mock

import helpers
from helpers import hook, lanes

# The lane the README lays on step 3, as the hook's command gives it.
WORDS = ["3:hands_off:git commit,git push"]
# The sentence of start_with laid on step 1, taking the script it runs.
BEGIN = "First run `scripts/log.py`."
# The changelog written by the Write tool, as the record holds it.
CHANGE = helpers.writing("CHANGELOG.md")
# What the subagent is told where step 3 no longer says the lane's sentence.
GONE = (
    "notes: step 3 of changelog-writer no longer says: Do not run `git commit` or `git push`."
    " Stop here and reply that lane:up must be run again on notes, so its lanes match its steps.\n"
)


class GuardTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        # Step 3 as lane:up writes it.
        self.write(self.agent_file, helpers.LAID)

    def guard(self, stream, words=(helpers.AGENT, *WORDS), entry="pretooluse.py"):
        """The event's entry, PreToolUse's where none is named, run as Claude Code runs it, on the
        stream, for the plugin, in this process so that the coverage of the test run counts it;
        what it exits with and what it writes on stderr."""
        script = os.path.join(helpers.CODE, entry)
        argv = mock.patch.object(sys, "argv", [script, *words])
        stdin = mock.patch.object(sys, "stdin", io.StringIO(stream))
        root = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": self.plugin})
        err = io.StringIO()
        with (
            argv,
            stdin,
            root,
            contextlib.redirect_stderr(err),
            self.assertRaises(SystemExit) as done,
        ):
            runpy.run_path(script, run_name="__main__")
        return done.exception.code, err.getvalue()


class TestStop(GuardTest):
    def test_a_command_the_step_says_not_to_run_is_stopped_with_its_sentence(self):
        # Given: hands_off on step 3 of changelog-writer
        # When: changelog-writer runs `git commit -m notes`
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin
        self.assertEqual(
            self.guard(self.stream("git commit -m notes")),
            (2, "notes: Do not run `git commit` or `git push`.\n"),
        )

    def test_a_call_the_sentence_allows_is_let_through(self):
        # Given: hands_off on step 3 of changelog-writer
        # When: changelog-writer runs `git status`
        # Then: the call goes on, nothing said
        self.assertEqual(self.guard(self.stream("git status")), (0, ""))

    def test_a_step_no_longer_saying_the_sentence_stops_the_call(self):
        # Given: step 3 changed by the building AI since the lane was laid
        self.write(self.agent_file, helpers.STEPS)
        # When: changelog-writer makes a call the hook watches, even one the lane allows
        # Then: the call is stopped, saying to have lane:up run again
        self.assertEqual(self.guard(self.stream("git status")), (2, GONE))


class TestStartWith(GuardTest):
    def setUp(self) -> None:
        super().setUp()
        # Step 1 with start_with laid on it, taking the script it runs.
        laid = helpers.LAID.replace("since the last release.", "since the last release. " + BEGIN)
        self.write(self.agent_file, laid)

    def started(self, command):
        return self.guard(self.stream(command), (helpers.AGENT, "1:start_with:scripts/log.py"))

    def test_a_first_call_running_anything_but_the_script_is_stopped_with_its_sentence(self):
        # Given: start_with on step 1 of changelog-writer, its record holding no call yet
        self.record([])
        # When: changelog-writer's first call runs something else
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin
        self.assertEqual(self.started("ls"), (2, f"notes: {BEGIN}\n"))

    def test_the_script_run_first_goes_on(self):
        # Given: start_with on step 1 of changelog-writer, its record holding no call yet
        self.record([])
        # When: its first call runs the script
        # Then: the call goes on, nothing said
        self.assertEqual(self.started(f"python3 {self.plugin}/scripts/log.py"), (0, ""))

    def test_a_call_after_the_script_ran_goes_on(self):
        # Given: start_with on step 1 of changelog-writer, its record holding the script run
        self.record([helpers.bash(f"python3 {self.plugin}/scripts/log.py")])
        # When: it makes any other call
        # Then: the call goes on, nothing said
        self.assertEqual(self.started("ls"), (0, ""))


class TestEnd(GuardTest):
    """The lanes held as the subagent is about to end: test_after on step 3, end_when on step 4."""

    TESTED = "After changing `CHANGELOG.md`, pass `python3 check.py`."
    ENDED = "End only once `CHANGELOG.md` is made."
    LAID = ("3:test_after:CHANGELOG.md,python3 check.py", "4:end_when:CHANGELOG.md")

    def setUp(self) -> None:
        super().setUp()
        laid = helpers.STEPS.replace("`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {self.TESTED}\n")
        laid = laid.replace("what you wrote.\n", f"what you wrote. {self.ENDED}\n")
        self.write(self.agent_file, laid)
        # The changelog there, as a write of it in the record leaves it.
        self.write(os.path.join(self.base, "CHANGELOG.md"), "- Added: lanes\n")

    def ended(self, calls, active=False, agent_type=helpers.AGENT):
        """The SubagentStop entry run on the lanes, the subagent about to end after the calls."""
        if calls is not None:
            self.record(calls)
        stream = json.dumps(self.stopped("Done.", active, agent_type))
        return self.guard(stream, (helpers.AGENT, *self.LAID), "subagentstop.py")

    def test_ending_with_a_change_not_passed_keeps_it_going_with_the_sentence(self):
        # Given: the changelog written and the check never run
        # When: changelog-writer is about to end
        # Then: it is kept going and told test_after's sentence headed by the plugin
        self.assertEqual(self.ended([CHANGE]), (2, f"notes: {self.TESTED}\n"))

    def test_ending_with_the_change_passed_and_the_output_made_ends(self):
        # Given: the changelog written, then the check run with no error
        # When: changelog-writer is about to end
        # Then: it ends, nothing said
        self.assertEqual(self.ended([CHANGE, helpers.bash("python3 check.py")]), (0, ""))

    def test_each_lane_not_kept_is_told(self):
        # Given: nothing written, the changelog there from before
        # When: changelog-writer is about to end
        # Then: it is told end_when's sentence alone, as no change waits on the check
        self.assertEqual(self.ended([]), (2, f"notes: {self.ENDED}\n"))

    def test_a_command_writing_the_output_that_a_hook_stopped_is_no_change(self):
        # Given: a command writing the changelog, stopped by a hook, so it never ran
        stopped = helpers.Failed("PreToolUse:Bash hook error: [python3 x.py]: notes: Write it.")
        calls = [("Bash", {"command": "echo x > CHANGELOG.md"}, stopped)]
        # When: changelog-writer is about to end
        # Then: it is not told test_after's sentence, as no change waits on the check
        self.assertEqual(self.ended(calls), (2, f"notes: {self.ENDED}\n"))

    def test_told_and_answering_in_words_alone_ends(self):
        # Given: a change not passed, told before, and answered with words alone since
        # When: changelog-writer, kept going by the stop hook, is about to end again
        # Then: it ends, nothing said, as it is told and never held for good
        self.assertEqual(self.ended([CHANGE, "told"], active=True), (0, ""))

    def test_told_and_working_since_is_told_again(self):
        # Given: a change not passed, told before, and the check run since, failing
        calls = [CHANGE, "told", helpers.failing("python3 check.py")]
        # When: changelog-writer, kept going by the stop hook, is about to end again
        # Then: it is told again
        self.assertEqual(self.ended(calls, active=True), (2, f"notes: {self.TESTED}\n"))

    def test_with_no_record_found_it_ends(self):
        # Given: no record of what changelog-writer did
        # When: it is about to end
        # Then: it ends, nothing said, as what it did is not known
        self.assertEqual(self.ended(None), (0, ""))

    def test_another_agent_ends(self):
        # Given: a change not passed
        # When: another agent is about to end
        # Then: it ends, nothing said
        self.assertEqual(self.ended([CHANGE], agent_type="notes:other"), (0, ""))

    def test_a_step_no_longer_saying_the_sentence_is_told_once(self):
        # Given: step 3 changed by the building AI since the lane was laid
        self.write(self.agent_file, helpers.STEPS)
        # When: changelog-writer is about to end, then again after answering in words alone
        # Then: it is told to reply that lane:up must be run again, then ends
        code, said = self.ended([CHANGE])
        self.assertEqual(code, 2)
        self.assertIn("lane:up must be run again on notes", said)
        self.assertEqual(self.ended([CHANGE, "told"], active=True), (0, ""))

    def test_every_item_is_told_on_an_item_unanswered(self):
        # Given: every_item on step 1, taking a review of the item B-1, and a reply not naming it
        sentence = "Answer every item of `review.md`."
        laid = helpers.STEPS.replace(
            "since the last release.", f"since the last release. {sentence}"
        )
        self.write(self.agent_file, laid)
        self.write(os.path.join(self.base, "review.md"), "- B-1: fix it\n")
        self.record([])
        # When: changelog-writer is about to end
        stream = json.dumps(self.stopped("Done."))
        words = (helpers.AGENT, "1:every_item:review.md")
        # Then: it is kept going and told the sentence
        self.assertEqual(self.guard(stream, words, "subagentstop.py"), (2, f"notes: {sentence}\n"))

    def test_lanes_given_to_the_entry_of_another_event_let_it_through_saying_so(self):
        wrong = {
            "a lane held on a tool call": ("subagentstop.py", "3:hands_off:git push"),
            "a lane held at the end": ("pretooluse.py", "3:test_after:CHANGELOG.md,make"),
            "fewer things than places": ("subagentstop.py", "3:test_after:CHANGELOG.md"),
        }
        for what, (entry, word) in wrong.items():
            with self.subTest(what=what):
                # Given: a hook's command giving its event's entry a lane not held on that event,
                # or taking fewer things than its wording has places
                # When: the entry is run by it
                code, said = self.guard(self.stream("ls"), (helpers.AGENT, word), entry)
                # Then: it exits 1, naming the lane and to have lane:up write the hooks again
                self.assertEqual(code, 1)
                self.assertIn(word, said)
                self.assertIn("run lane:up again", said)


class TestRunValues(GuardTest):
    """Lanes taking a value given for each run, `{work}`, from the JSON the subagent starts from."""

    WRITE = "Write only `{work}`."
    # The run's JSON, as the subagent's prompt or a script's print gives it, naming the work and a
    # file the lane does not take.
    RUN = '{"work": ["a.md", "b.md"], "has": "h.md"}'
    TOLD = "notes: Write only `{work}`.\n`{work}` is `a.md`, `b.md`.\n"

    def setUp(self) -> None:
        super().setUp()
        laid = helpers.STEPS.replace("`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {self.WRITE}\n")
        self.write(self.agent_file, laid)

    def wrote(self, path, words=(helpers.AGENT, "3:write_only:{work}")):
        """The guard on a Write of the path."""
        event = self.called("Write", {"file_path": path, "content": "x"})
        return self.guard(json.dumps(event), words)

    def test_a_write_of_a_file_the_runs_value_does_not_name_is_told_with_the_value(self):
        # Given: write_only taking `{work}`, the prompt naming the work
        self.record([], self.RUN)
        # When: changelog-writer writes another file
        # Then: it is stopped, told the sentence as its step says it, the value on the next line
        self.assertEqual(self.wrote("c.md"), (2, self.TOLD))

    def test_a_write_of_a_file_the_runs_value_names_goes_on(self):
        # Given: write_only taking `{work}`, the prompt naming the work
        self.record([], self.RUN)
        # When: changelog-writer writes a file of the work
        # Then: it goes on, nothing said
        self.assertEqual(self.wrote("b.md"), (0, ""))

    def test_until_the_value_is_given_every_call_goes_on(self):
        for prompt in (helpers.PROMPT, '{"has": "a.md"}', '{"work": 1}'):
            with self.subTest(prompt=prompt):
                # Given: a prompt of words, of JSON naming no work, or naming it by no text
                self.record([], prompt)
                # When: changelog-writer writes any file
                # Then: it goes on, nothing said
                self.assertEqual(self.wrote("c.md"), (0, ""))

    def test_with_no_record_found_every_call_goes_on(self):
        # Given: no record of what changelog-writer was given
        # When: it writes any file
        # Then: it goes on, nothing said
        self.assertEqual(self.wrote("c.md"), (0, ""))

    def test_a_script_start_with_takes_gives_the_value_over_the_prompt(self):
        # Given: start_with laid on step 1, taking `scripts/given.py`, which printed the work
        # after the prompt named another
        laid = self.read(self.agent_file).replace(
            "release.", "release. " + BEGIN.replace("log", "given")
        )
        self.write(self.agent_file, laid)
        command = (
            'exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" notes:changelog-writer'
            " 1:start_with:scripts/given.py 3:write_only:{work}"
        )
        hooks = {"hooks": {"PreToolUse": [{"hooks": [{"command": command}]}]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        run = ("Bash", {"command": f"python3 {self.plugin}/scripts/given.py"}, '{"work": "c.md"}')
        self.record([run], self.RUN)
        # When: changelog-writer writes the file the script named, then one the prompt named
        words = (helpers.AGENT, "1:start_with:scripts/given.py", "3:write_only:{work}")
        # Then: the first goes on, and the second is told with the script's value
        self.assertEqual(self.wrote("c.md", words), (0, ""))
        told = "notes: Write only `{work}`.\n`{work}` is `c.md`.\n"
        self.assertEqual(self.wrote("a.md", words), (2, told))

    def test_an_output_of_a_list_is_held_to_its_form_one_by_one_the_point_told_last(self):
        # Given: in_form taking `{work}` and a form, the prompt naming two JSON outputs
        form = "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), {"type": "object"})
        sentence = f"Write `{{work}}` in the form of `{form}`."
        self.write(
            self.agent_file,
            helpers.STEPS.replace("`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {sentence}\n"),
        )
        self.record([], '{"work": ["a.json", "b.json"]}')
        # When: changelog-writer writes the second output out of the form
        event = self.called("Write", {"file_path": "b.json", "content": "[]"})
        said = self.guard(json.dumps(event), (helpers.AGENT, f"3:in_form:{{work}},{form}"))
        # Then: it is told the sentence, the value, then the point it is out by
        expanded = sentence.replace("${CLAUDE_PLUGIN_ROOT}", self.plugin)
        value = "`{work}` is `a.json`, `b.json`."
        self.assertEqual(
            said, (2, f"notes: {expanded}\n{value}\n$: expected an object, found []\n")
        )

    def test_a_lane_held_at_the_end_takes_the_value_too(self):
        # Given: end_when taking `{work}` on step 4, the prompt naming the work, none made
        ended = "End only once `{work}` is made."
        self.write(
            self.agent_file,
            helpers.STEPS.replace("what you wrote.\n", f"what you wrote. {ended}\n"),
        )
        self.record([], self.RUN)
        # When: changelog-writer is about to end
        stream = json.dumps(self.stopped("Done."))
        said = self.guard(stream, (helpers.AGENT, "4:end_when:{work}"), "subagentstop.py")
        # Then: it is kept going, told the sentence and the value
        self.assertEqual(said, (2, f"notes: {ended}\n`{{work}}` is `a.md`, `b.md`.\n"))


class TestOtherAgents(GuardTest):
    def test_the_same_call_in_another_subagent_or_the_main_conversation_goes_on(self):
        for agent_type in ("notes:other", "other:changelog-writer", "changelog-writer", None):
            with self.subTest(agent_type=agent_type):
                # Given: hands_off laid in changelog-writer
                # When: a call it would stop is made where another agent runs
                # Then: it goes on, nothing said
                stream = self.stream("git commit -m notes", agent_type)
                self.assertEqual(self.guard(stream), (0, ""))


class TestCommandLine(GuardTest):
    def test_a_command_line_not_as_lane_up_writes_it_lets_the_call_through_saying_so(self):
        wrong = {
            "no subagent": ([], "gives no subagent"),
            "a subagent of no plugin": (["changelog-writer", *WORDS], "gives no subagent"),
            "a lane of no step": ([helpers.AGENT, "x:hands_off:git push"], "x:hands_off:git push"),
            "a lane lane has not": ([helpers.AGENT, "3:no_lane:git push"], "3:no_lane:git push"),
            "a lane taking nothing": ([helpers.AGENT, "3:hands_off:"], "3:hands_off:"),
            "a lane taking an empty thing": ([helpers.AGENT, "3:hands_off:a,"], "3:hands_off:a,"),
            "a lane of two parts": ([helpers.AGENT, "3:hands_off"], "3:hands_off"),
            "a lane taking too few": ([helpers.AGENT, "3:in_form:a.json"], "3:in_form:a.json"),
        }
        for what, (words, named) in wrong.items():
            with self.subTest(what=what):
                # Given: a hook's command edited out of the form lane:up writes
                # When: the guard is run by it
                code, said = self.guard(self.stream("git commit"), words)
                # Then: it exits 1, on which Claude Code goes on and shows the user what was
                # wrong, naming it, and to have lane:up write the hooks again
                self.assertEqual(code, 1)
                self.assertIn(named, said)
                self.assertTrue(said.startswith("lane: ") and "run lane:up again" in said, said)


class TestRun(helpers.PluginTest):
    """hook.run given the subagent its checks act in."""

    def ran(self, agent_type):
        checks = [lanes.Laid(self.plugin, helpers.AGENT, 1, "hands_off", ["x"])]
        err = io.StringIO()
        stream = io.StringIO(self.stream("x", agent_type))
        return hook.run("notes", checks, stream, err, helpers.AGENT), err.getvalue()

    def test_checks_run_on_an_event_of_the_subagent_named(self):
        # Given: a check whose step does not say its sentence, which stops every call
        # When: the entry runs it on an event of the subagent named
        # Then: it stops the call
        self.assertEqual(self.ran(helpers.AGENT)[0], hook.STOPPED)

    def test_checks_do_not_run_on_an_event_of_another_agent(self):
        # Given: the same check
        # When: the entry runs it on an event of another agent
        # Then: it lets the call go on, nothing said
        self.assertEqual(self.ran("notes:other"), (0, ""))
