"""The guard: in the subagent its command names, and there alone, a call that drifts from a lane is
stopped and the subagent told `<plugin>: <sentence>`; a lane whose step no longer says its sentence
stops the call and says to have lane:up run again."""

import contextlib
import io
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

    def guard(self, stream, words=(helpers.AGENT, *WORDS)):
        """The PreToolUse entry run as Claude Code runs it, on the stream, for the plugin, in this
        process so that the coverage of the test run counts it; what it exits with and what it
        writes on stderr."""
        script = os.path.join(helpers.CODE, "pretooluse.py")
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
        # Given: step 3 changed by the builder since the lane was laid
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
