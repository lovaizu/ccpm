"""What each hook's command runs: the event Claude Code hands on stdin read, the guard asked where
the event is of a subagent of the plugin, and its answer given in Claude Code's JSON output of the
event: a break denied with its sentence, the next start added as context, an end kept going, an
error told the user too."""

import io
import json
import os
import runpy
import unittest
from unittest import mock

import helpers
from helpers import hook

AGENT_TYPE = "changelog:writer"
RUN_BREAK = (
    f"changelog: {helpers.RUN}\nThe commands you may run, each word for word: `git log --oneline`."
)


class HookTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay()

    def answered(
        self, given: object, argv: tuple = ("changelog",), held: str = "PreToolUse"
    ) -> dict:
        """What the hook of the event held, PreToolUse by default, answers on stdout, given the
        event, as JSON or as the text itself, with the command's words."""
        text = given if isinstance(given, str) else json.dumps(given)
        out = io.StringIO()
        hook.main(held, list(argv), io.StringIO(text), out, self.plugin)
        return helpers.answer(out.getvalue())


def denied(reason: str, user: str = "") -> dict:
    """The answer denying the call with the reason, telling the user where there is anything."""
    found = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    return {"systemMessage": user, **found} if user else found


class TestAnswer(HookTest):
    def test_a_call_its_lanes_allow_is_answered_nothing(self):
        # Given: writer with the README's lanes laid
        # When: it runs git log --oneline
        # Then: the hook prints nothing, so the call goes on
        self.assertEqual(self.answered(self.bash("git log --oneline")), {})

    def test_a_break_is_denied_with_the_sentence_headed_by_the_plugins_name(self):
        # Given: writer with the README's lanes laid
        # When: it runs git commit
        # Then: the call is denied, the reason the sentence headed changelog:, the user told
        # nothing, as a break is the subagent's to put right
        self.assertEqual(self.answered(self.bash("git commit -m m")), denied(RUN_BREAK))

    def test_an_error_is_told_the_subagent_and_the_user(self):
        # Given: hooks/lanes.json removed
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        # When: writer runs git log --oneline
        found = self.answered(self.bash("git log --oneline"))
        # Then: the call is denied, and the user told the same, headed changelog:
        reason = found["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertTrue(reason.startswith("changelog: lane cannot check the lanes of writer:"))
        self.assertEqual(found, denied(reason, reason))

    def test_a_call_of_no_subagent_of_the_plugin_is_answered_nothing(self):
        for agent in (None, "other:writer", "changelog-x:writer", "general-purpose"):
            with self.subTest(agent=agent):
                # Given: writer with the README's lanes laid
                # When: the main conversation, a subagent of another plugin, one of a plugin
                # whose name begins with changelog, or a built-in subagent runs git commit
                # Then: the hook prints nothing, as lane checks this plugin's subagents alone
                self.assertEqual(self.answered(self.bash("git commit", agent)), {})


class TestEvent(HookTest):
    def test_an_event_out_of_its_documented_fields_is_an_error_for_claude_code(self):
        good = self.bash("ls")
        for event, wrong in (
            ({**good, "cwd": os.path.join(self.base, "gone")}, "$.cwd: expected a folder"),
            ({**good, "cwd": 1}, "$.cwd: expected a string"),
            ({**good, "tool_input": "ls"}, "$.tool_input: expected an object"),
            ({**good, "hook_event_name": "PostToolUse"}, "$.hook_event_name: expected"),
            ({k: v for k, v in good.items() if k != "tool_name"}, 'expected the key "tool_name"'),
        ):
            with self.subTest(wrong=wrong):
                # Given: writer's event with a folder not there, a folder not text, an input not
                # an object, another event's name, or no tool
                # When: the hook is handed it
                found = self.answered(event)
                # Then: the call is denied, telling what is wrong, for Claude Code to fix
                reason = found["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertIn("the hook was handed no event as Claude Code hands it, ", reason)
                self.assertIn(wrong, reason)
                self.assertIn("`claude update`", reason)

    def test_text_that_is_no_json_object_is_an_error_naming_this_hook(self):
        for text in ("not json", "[1]"):
            with self.subTest(text=text):
                # Given: the hook handed no JSON, or JSON that is no object
                # When: it is run
                found = self.answered(text)
                # Then: the call is denied, as no subagent can be told from it, and the user told
                reason = found["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertTrue(
                    reason.startswith(
                        "changelog: lane cannot check the lanes of this hook: it was handed no"
                        " JSON object."
                    ),
                    reason,
                )
                self.assertEqual(found["systemMessage"], reason)


class TestCommand(HookTest):
    def test_a_command_not_naming_the_plugin_stops_every_subagents_call(self):
        for argv in ((), ("changelog", "x"), ("change log",), ("a/b",)):
            with self.subTest(argv=argv):
                # Given: a hook's command giving no name, two words, or no name of a plugin
                # When: writer runs git log --oneline
                found = self.answered(self.bash("git log --oneline"), argv)
                # Then: the call is denied, headed lane:, as the plugin is not known
                reason = found["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertTrue(
                    reason.startswith("lane: lane cannot check the lanes of this hook: its command")
                )
                self.assertIn("`lay.py write`", reason)

    def test_a_command_not_naming_the_plugin_lets_the_main_conversation_go_on(self):
        # Given: a hook's command giving no name
        # When: the main conversation runs a command
        # Then: nothing is printed, as lane checks subagents alone
        self.assertEqual(self.answered(self.bash("ls", None), ()), {})


class TestEntry(HookTest):
    def test_pretooluse_py_runs_the_hook_on_its_event_with_claude_codes_plugin_folder(self):
        # Given: writer running git commit, and the plugin's folder in CLAUDE_PLUGIN_ROOT
        stdin, out = io.StringIO(json.dumps(self.bash("git commit"))), io.StringIO()
        env = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": self.plugin})
        argv = mock.patch("sys.argv", ["pretooluse.py", "changelog"])
        # When: pretooluse.py runs as Claude Code runs it
        with env, argv, mock.patch("sys.stdin", stdin), mock.patch("sys.stdout", out):
            runpy.run_path(os.path.join(helpers.CODE, "pretooluse.py"), run_name="__main__")
        # Then: it answers as the hook does
        self.assertEqual(helpers.answer(out.getvalue()), denied(RUN_BREAK))


class TestRoutes(HookTest):
    def setUp(self) -> None:
        super().setUp()
        self.route()

    def test_the_next_start_is_added_as_context_as_lead_starts_and_its_starts_come_back(self):
        start = self.subagent("SubagentStart", "lead", "lead1")
        failed = {**self.start("writer", "PostToolUseFailure"), "error": "e", "is_interrupt": False}
        for event, held in (
            (start, "SubagentStart"),
            (failed, "PostToolUseFailure"),
            (
                self.start("writer", "PostToolUse", helpers.back("w1", "async_launched")),
                "PostToolUse",
            ),
        ):
            with self.subTest(held=held):
                # Given: the routes laid
                # When: lead starts, its start of writer fails, or comes back launched
                found = self.answered(event, held=held)
                # Then: the line is added as context of the event, headed changelog:
                self.assertEqual(found["hookSpecificOutput"]["hookEventName"], held)
                self.assertTrue(
                    found["hookSpecificOutput"]["additionalContext"].startswith("changelog: ")
                )
                self.assertNotIn("systemMessage", found)

    def test_a_start_while_one_runs_in_the_background_is_denied(self):
        # Given: lead's start of writer launched in the background
        back = self.start("writer", "PostToolUse", helpers.back("w1", "async_launched"))
        self.answered(back, held="PostToolUse")
        # When: lead's start of reviewer reaches the hook, read from its JSON
        found = self.answered(self.start("reviewer"))
        # Then: it is denied, telling lead to wait
        reason = found["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("Wait for `changelog:writer` to end", reason)

    def test_a_subagent_ending_with_no_result_is_blocked_with_its_sentence(self):
        # Given: writer giving no result
        # When: it is about to end
        found = self.answered(self.subagent("SubagentStop", "writer", "a1"), held="SubagentStop")
        # Then: it is blocked, told its last step's sentence headed changelog:
        gives = f"python3 {self.plugin}/hooks/lane/result.py writer written"
        self.assertEqual(
            found, {"decision": "block", "reason": f"changelog: End by running `{gives}`."}
        )

    def test_an_unnamed_start_is_denied_with_the_sentence_and_the_start_each_line_headed(self):
        # Given: writer due
        # When: lead starts reviewer
        # Then: it is denied, told the sentence and on the next line the start, each headed
        self.assertEqual(
            self.answered(self.start("reviewer")),
            denied(f"changelog: {helpers.FOLLOW}\nchangelog: Start `changelog:writer`."),
        )

    def test_an_error_at_another_event_is_told_the_user_too(self):
        # Given: hooks/lanes.json removed
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        # When: lead starts
        found = self.answered(self.subagent("SubagentStart", "lead", "lead1"), held="SubagentStart")
        # Then: the error is the context and the user's message alike
        told = found["hookSpecificOutput"]["additionalContext"]
        self.assertTrue(told.startswith("changelog: lane cannot check the lanes of lead:"))
        self.assertEqual(found["systemMessage"], told)

    def test_an_error_of_the_guard_at_subagentstop_is_told_once(self):
        # Given: hooks/lanes.json removed
        os.remove(os.path.join(self.plugin, "hooks", "lanes.json"))
        for active, blocked in ((False, True), (True, False)):
            with self.subTest(active=active):
                # When: writer is about to end, kept going by a stop hook before or not
                stop = self.subagent("SubagentStop", "writer", "a1", active)
                found = self.answered(stop, held="SubagentStop")
                # Then: it is blocked with the error the first time, and ends the second
                self.assertEqual("decision" in found, blocked)

    def test_an_error_before_the_guard_at_subagentstop_is_told_once(self):
        stop = self.subagent("SubagentStop", "writer", "a1")
        for given, argv, blocked in (
            ("x", ("changelog",), True),
            (stop, (), True),
            ({**stop, "stop_hook_active": True}, (), False),
        ):
            with self.subTest(given=given, argv=argv):
                # Given: SubagentStop handed no JSON object, or by a command not naming the
                # plugin, kept going by a stop hook before or not
                # When: the hook runs
                found = self.answered(given, argv, "SubagentStop")
                # Then: the end is blocked with the error, but where it was kept going before
                self.assertEqual("decision" in found, blocked)

    def test_an_event_out_of_its_fields_is_an_error_for_claude_code(self):
        stop = self.subagent("SubagentStop", "writer", "a1")
        for event, held, wrong in (
            ({**stop, "stop_hook_active": "no"}, "SubagentStop", "$.stop_hook_active"),
            ({**stop, "stop_hook_active": 1}, "SubagentStop", "$.stop_hook_active"),
            ({**stop, "agent_id": "../x"}, "SubagentStop", "$.agent_id"),
            (self.start("writer", "PostToolUse"), "PostToolUse", '"tool_response"'),
        ):
            with self.subTest(wrong=wrong):
                # Given: an event of a wrong field, an ID naming another folder, or no response
                # When: the hook is handed it
                found = self.answered(event, held=held)
                # Then: it tells what is wrong
                self.assertIn(wrong, found["systemMessage"])


class TestDependency(HookTest):
    def test_an_event_of_a_dependencys_subagent_the_routes_name_reaches_the_guard(self):
        # Given: routes to checker's examiner
        self.depend()
        # When: examiner is about to end with no result
        stop = self.subagent("SubagentStop", "checker:examiner", "e1")
        found = self.answered(stop, held="SubagentStop")
        # Then: the guard keeps it going, headed by changelog's name
        self.assertEqual(found["decision"], "block")
        self.assertTrue(found["reason"].startswith("changelog: End by running "), found)

    def test_an_event_of_another_plugins_subagent_no_route_names_is_answered_nothing(self):
        # Given: routes to checker's examiner
        self.depend()
        # When: checker's linter is about to end
        # Then: nothing is said
        stop = self.subagent("SubagentStop", "checker:linter", "x1")
        self.assertEqual(self.answered(stop, held="SubagentStop"), {})


class TestEntries(HookTest):
    def test_each_events_script_runs_the_hook_on_its_event(self):
        self.route()
        for script, held, event in (
            ("posttooluse", "PostToolUse", self.came_back("ls")),
            (
                "posttoolusefailure",
                "PostToolUseFailure",
                self.bash("ls", held="PostToolUseFailure"),
            ),
            ("subagentstart", "SubagentStart", self.subagent("SubagentStart", "lead", "lead1")),
            ("subagentstop", "SubagentStop", self.subagent("SubagentStop", "lead", "lead1")),
        ):
            with self.subTest(script=script):
                # Given: the event, and the plugin's folder in CLAUDE_PLUGIN_ROOT
                stdin, out = io.StringIO(json.dumps(event)), io.StringIO()
                env = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": self.plugin})
                argv = mock.patch("sys.argv", [f"{script}.py", "changelog"])
                # When: the event's script runs as Claude Code runs it
                with env, argv, mock.patch("sys.stdin", stdin), mock.patch("sys.stdout", out):
                    runpy.run_path(os.path.join(helpers.CODE, f"{script}.py"), run_name="__main__")
                # Then: it answers as the hook does on that event
                expected = io.StringIO()
                hook.main(
                    held, ["changelog"], io.StringIO(json.dumps(event)), expected, self.plugin
                )
                self.assertEqual(out.getvalue(), expected.getvalue())


class TestU3(HookTest):
    def test_a_held_command_is_asked_of_the_person_with_its_sentence(self):
        # Given: writer holding git push for the person's approval
        self.lay_lanes([{"step": 2, "lanes": [{"lane": "hold", "takes": ["git push"]}]}])
        # When: it runs git push
        found = self.answered(self.bash("git push"))
        # Then: Claude Code is asked to put it to the person, with the sentence headed changelog:
        said = "changelog: Run `git push` only with the person's approval."
        self.assertEqual(
            found,
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": said,
                }
            },
        )

    def test_a_part_is_given_as_it_is_as_the_subagent_starts(self):
        # Given: writer's entry naming its part
        part = os.path.join(self.plugin, "prompts", "writer.md")
        self.write(part, helpers.LAID.split("---\n\n", 1)[1])
        self.write(self.agent_file, helpers.PART_ENTRY.format(name="writer"))
        # When: writer starts
        start = self.subagent("SubagentStart", "writer", "a1")
        found = self.answered(start, held="SubagentStart")
        # Then: the part is added as context, headed by nothing
        context = found["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(context, self.read(part))

    def test_an_agent_call_of_the_main_conversation_gives_its_prompt_to_the_run_it_started(self):
        # Given: writer laid, and the main conversation's Agent call starting it
        given = {"prompt": "p", "subagent_type": AGENT_TYPE}
        call = {**self.event("Agent", given, None), "tool_use_id": "t1"}
        # When: the call is made, writer starts, and the call comes back launched in the
        # background
        self.assertEqual(self.answered(call), {})
        self.answered(self.subagent("SubagentStart", "writer", "a1"), held="SubagentStart")
        self.assertIsNone(helpers.called.texts(helpers.KEPT, "a1"))
        back = {
            **self.event("Agent", given, None, "PostToolUse"),
            "tool_use_id": "t1",
            "tool_response": helpers.back("a1", "async_launched"),
        }
        self.assertEqual(self.answered(back, held="PostToolUse"), {})
        # Then: writer's run of the ID it gave is given the call's prompt
        self.assertEqual(helpers.called.texts(helpers.KEPT, "a1"), ["p"])

    def test_a_start_of_leads_coming_back_gives_its_prompt_to_the_run_it_started(self):
        # Given: the routes laid
        self.route()
        # When: lead's start of writer comes back launched in the background, lead told to wait
        back = self.start("writer", "PostToolUse", helpers.back("w1", "async_launched"))
        found = self.answered(back, held="PostToolUse")
        self.assertIn("Wait for", found["hookSpecificOutput"]["additionalContext"])
        # Then: writer's run of the ID it gave is given the call's prompt
        self.assertEqual(helpers.called.texts(helpers.KEPT, "w1"), ["p"])

    def test_a_message_is_kept_where_its_call_goes_on_alone(self):
        # Given: the routes laid, writer due, and a run of writer given its prompt
        self.route()
        helpers.called.keep(helpers.KEPT, "w1", helpers.called.given("p"))
        sent = {"to": "w1", "message": "m"}
        # When: lead sends it a message, which is stopped as writer's start is due, and the main
        # conversation sends it one, which goes on
        lead = {**self.event("SendMessage", sent, "changelog:lead", agent_id="lead1")}
        self.assertIn("hookSpecificOutput", self.answered(lead))
        main = {**self.event("SendMessage", {**sent, "message": "n"}, None)}
        self.assertEqual(self.answered(main), {})
        # Then: the main conversation's alone is kept
        self.assertEqual(helpers.called.texts(helpers.KEPT, "w1"), ["p", "n"])

    def test_an_orchestrator_let_end_with_a_start_due_tells_the_operator_alone(self):
        # Given: the routes laid, writer due
        self.route()
        # When: lead, kept going once, is about to end again
        stop = self.subagent("SubagentStop", "lead", "lead1", active=True)
        found = self.answered(stop, held="SubagentStop")
        # Then: it ends, and the operator is told what is left, headed by the plugin's name
        self.assertEqual(
            found,
            {
                "systemMessage": "changelog: lane let lead end with `changelog:writer` still"
                " due: the maker of changelog must fix step 1 of lead in agents/lead.md, which"
                " starts it."
            },
        )

    def test_an_agent_call_stopped_keeps_nothing(self):
        # Given: the routes laid, writer due
        self.route()
        # When: lead's start of reviewer is stopped
        self.answered({**self.start("reviewer"), "tool_use_id": "t1"})
        # Then: nothing is kept for any run of reviewer
        self.answered(self.subagent("SubagentStart", "reviewer", "r1"), held="SubagentStart")
        self.assertIsNone(helpers.called.texts(helpers.KEPT, "r1"))


if __name__ == "__main__":
    unittest.main()
