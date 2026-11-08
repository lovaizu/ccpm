"""The cases of guard.py's contract for a run of the skill, as the architecture's sequences "S3: a
run that passes on each start as given" and "S3: a result given" draw them."""

import json
import os

import helpers
from helpers import exchange, guard

FOLLOW = helpers.FOLLOW
RESULT = helpers.RESULT
WAIT = "Wait for `changelog:writer` to end: you are told the next start once it has."
WAIT_ALL = (
    "Wait for every run of `changelog:reviewer` to end: you are told the next start once each has."
)
NO_START = (
    "changelog: Start no subagent of this plugin: only the main conversation starts one, with what"
    " the plugin gives it. Reply with what you would pass on, and end."
)


class RunTest(helpers.PluginTest):
    def setUp(self):
        super().setUp()
        helpers.changelog(self.root, with_routes=True)
        self.agents = 0

    def routes(self, **more):
        """Lays the routes with the changes given."""
        path = os.path.join(self.root, "hooks", "lanes.json")
        data = json.loads(self.read(path))
        data["routes"] = {**helpers.ROUTES, **more}
        helpers.write(path, json.dumps(data))

    def send(self, name, agent=None, kind=None, **fields):
        event = exchange.Event(
            name=name, session="s1", cwd=self.project, agent_id=agent, agent_type=kind, **fields
        )
        return guard.answer("changelog", self.root, self.project, event)

    def typed(self, command="changelog:write"):
        return self.send("UserPromptExpansion", command=command, prompt=f"/{command}")

    def pre(self, tool, **given):
        return self.send("PreToolUse", tool=tool, tool_input=given)

    def post(self, tool, response, **given):
        return self.send("PostToolUse", tool=tool, tool_input=given, tool_response=response)

    def start(self, role, prompt="go", status="async_launched"):
        """The main conversation's Agent call of the role: its PreToolUse, then, where it goes on,
        its PostToolUse. It gives the two answers and the start's ID."""
        self.agents += 1
        agent = f"a{self.agents}"
        given = {"subagent_type": f"changelog:{role}", "prompt": prompt, "description": "d"}
        before = self.pre("Agent", **given)
        if before.deny:
            return before, None, None
        after = self.post("Agent", {"status": status, "agentId": agent}, **given)
        return before, after, agent

    def give(self, agent, role, result):
        """The role's run of the result script: its PreToolUse, then its PostToolUse."""
        bash = {"command": f"python3 {self.root}/hooks/lane/result.py {role} {result}"}
        before = self.send("PreToolUse", agent, f"changelog:{role}", tool="Bash", tool_input=bash)
        if not before.deny:
            self.send(
                "PostToolUse",
                agent,
                f"changelog:{role}",
                tool="Bash",
                tool_input=bash,
                tool_response={"stdout": ""},
            )
        return before

    def end(self, agent, role, again=False):
        return self.send("SubagentStop", agent, f"changelog:{role}", stop_active=again)

    def notified(self, agent):
        return self.send(
            "UserPromptSubmit",
            prompt=f"<task-notification>\n<task-id>{agent}</task-id>\n</task-notification>",
        )

    def ran(self, role, result):
        """A start of the role that gives the result and ends, and the context the main
        conversation gets as its end comes back."""
        _, _, agent = self.start(role)
        self.give(agent, role, result)
        self.end(agent, role)
        return self.notified(agent).context


class TestBegin(RunTest):
    def test_the_skills_command_typed_begins_a_run_with_the_first_start(self):
        self.assertEqual(self.typed().context, "changelog: Start `changelog:writer`.")

    def test_the_skill_called_by_an_ai_begins_a_run_with_the_first_start(self):
        found = self.post(
            "Skill", {"success": True, "commandName": "changelog:write"}, skill="changelog:write"
        )
        self.assertEqual(found.context, "changelog: Start `changelog:writer`.")

    def test_another_command_begins_no_run(self):
        self.assertEqual(self.typed("changelog:other"), exchange.Answer())

    def test_the_skill_called_again_while_its_run_goes_on_begins_no_other(self):
        self.typed()
        self.start("writer")
        self.assertEqual(self.typed(), exchange.Answer())

    def test_routes_with_no_step_tell_their_sentence_and_the_skills_result_as_the_run_begins(self):
        path = os.path.join(self.root, "hooks", "lanes.json")
        data = json.loads(self.read(path))
        del data["routes"]["step"]
        helpers.write(path, json.dumps(data))
        self.assertEqual(
            self.typed().context,
            f"changelog: {FOLLOW}\nchangelog: End by running `{RESULT} write good`.{helpers.ENDS}\n"
            "changelog: Start `changelog:writer`.",
        )

    def test_routes_with_a_command_tell_it_beside_the_first_start(self):
        self.routes(command="python3 ${CLAUDE_PLUGIN_ROOT}/s.py")
        self.assertEqual(
            self.typed().context,
            f"changelog: Start `changelog:writer`. Run `python3 {self.root}/s.py writer` first, and"
            " start it with what it prints as its prompt, word for word.",
        )

    def test_a_skill_step_no_longer_saying_the_routes_sentence_begins_no_run(self):
        path = os.path.join(self.root, "skills", "write", "SKILL.md")
        helpers.write(path, helpers.SKILL)
        found = self.typed()
        told = (
            "changelog: lane cannot check follow_routes on step 1 of write: step 1 no longer says"
            f' "{FOLLOW}". Tell the user: the maker of changelog must lay its lanes again with'
            " Lane's lay.py write."
        )
        self.assertEqual((found.context, found.tell), (told, told))

    def test_lanes_laid_that_cannot_be_read_tell_the_main_conversation_at_the_skills_command(self):
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), "{")
        self.assertIn(
            "changelog: lane cannot check the routes of write: ", self.typed().context or ""
        )


class TestBeginFaults(RunTest):
    def test_a_plugin_with_no_routes_begins_no_run(self):
        path = os.path.join(self.root, "hooks", "lanes.json")
        helpers.write(path, json.dumps({"subagents": [helpers.WRITER_LANES]}))
        self.assertEqual(self.typed(), exchange.Answer())

    def test_a_skill_of_another_plugin_begins_no_run(self):
        found = self.post("Skill", {"success": True}, skill="other:write")
        self.assertEqual(found, exchange.Answer())

    def test_a_skill_whose_file_is_gone_begins_no_run(self):
        os.remove(os.path.join(self.root, "skills", "write", "SKILL.md"))
        self.assertIn(
            "changelog: lane cannot check follow_routes on step 1 of write: ",
            self.typed().context or "",
        )

    def test_a_skill_that_no_longer_holds_the_routes_step_begins_no_run(self):
        self.routes(step=2)
        path = os.path.join(self.root, "skills", "write", "SKILL.md")
        helpers.write(path, helpers.SKILL_ROUTED.split("2. ")[0])
        self.assertIn(
            "follow_routes on step 2 of write: the steps hold no step 2.",
            self.typed().context or "",
        )


class TestOutside(RunTest):
    def test_a_start_outside_a_run_goes_on(self):
        self.assertEqual(
            self.pre("Agent", subagent_type="changelog:reviewer", prompt="p"), exchange.Answer()
        )

    def test_the_end_of_a_turn_outside_a_run_goes_on(self):
        self.assertEqual(self.send("Stop"), exchange.Answer())

    def test_a_prompt_outside_a_run_hears_nothing(self):
        self.assertEqual(self.send("UserPromptSubmit", prompt="hi"), exchange.Answer())


class TestStarts(RunTest):
    def setUp(self):
        super().setUp()
        self.typed()

    def test_a_prompt_before_the_first_start_hears_it(self):
        self.assertEqual(
            self.send("UserPromptSubmit", prompt="go on").context,
            "changelog: Start `changelog:writer`.",
        )

    def test_another_tool_of_the_main_conversation_goes_on(self):
        self.assertEqual(self.pre("Read", file_path="a"), exchange.Answer())

    def test_another_tool_that_comes_back_is_kept_as_nothing(self):
        self.assertEqual(self.post("Bash", {"stdout": ""}, command="ls"), exchange.Answer())

    def test_another_command_that_expands_within_the_run_hears_nothing(self):
        self.assertEqual(self.typed("other:skill"), exchange.Answer())

    def test_a_start_of_another_plugins_subagent_that_comes_back_is_not_kept(self):
        self.post("Agent", {"status": "async_launched", "agentId": "x"}, subagent_type="Explore")
        self.assertEqual(self.start("writer")[0], exchange.Answer())

    def test_a_message_to_a_start_outside_the_run_goes_on(self):
        self.assertEqual(self.pre("SendMessage", to="x", message="m"), exchange.Answer())

    def test_a_message_to_a_start_outside_the_run_that_comes_back_is_not_kept(self):
        self.post("SendMessage", {}, to="x", message="m")
        self.assertEqual(self.start("writer")[0], exchange.Answer())

    def test_lanes_laid_that_cannot_be_read_within_the_run_stop_a_start(self):
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), "{")
        self.assertIn(
            "changelog: lane cannot check the routes of write: ", self.start("writer")[0].deny or ""
        )

    def test_lanes_laid_that_cannot_be_read_within_the_run_let_the_turn_end_and_tell_why(self):
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), "{")
        found = self.send("Stop")
        self.assertEqual(
            (found.block, (found.tell or "")[:48]),
            (None, "changelog: lane cannot check the routes of write"),
        )

    def test_the_start_due_goes_on_and_is_told_to_wait(self):
        before, after, _ = self.start("writer")
        self.assertEqual(
            (before, after.context if after else None),
            (
                exchange.Answer(),
                f"changelog: {WAIT}",
            ),
        )

    def test_a_start_not_due_is_denied_with_the_start_due(self):
        before, _, _ = self.start("reviewer")
        self.assertEqual(before.deny, f"changelog: {FOLLOW}\nStart `changelog:writer`.")

    def test_a_start_while_another_runs_is_denied_with_the_wait(self):
        self.start("writer")
        before, _, _ = self.start("reviewer")
        self.assertEqual(
            before.deny,
            f"changelog: {FOLLOW}\n{WAIT}",
        )

    def test_a_second_start_of_a_role_that_doesnt_fan_out_is_denied_with_the_wait(self):
        self.start("writer")
        self.assertIsNotNone(self.start("writer")[0].deny)

    def test_a_start_of_another_plugins_subagent_goes_on(self):
        self.assertEqual(self.pre("Agent", subagent_type="Explore", prompt="p"), exchange.Answer())

    def test_a_start_that_comes_back_in_no_documented_form_keeps_it_due(self):
        _, after, _ = self.start("writer", status="weird")
        told = (
            "changelog: lane cannot check the routes of write: the Agent call came back with the"
            " status `weird`, where Claude Code documents async_launched or completed. Tell the"
            " user: Anthropic must fix Claude Code, whose hook input isn't as its documentation"
            " gives it."
        )
        self.assertEqual((after.context, after.tell) if after else None, (told, told))
        self.assertEqual(self.start("writer")[0], exchange.Answer())

    def test_a_start_that_ran_in_the_foreground_counts_as_it_comes_back(self):
        given = {"subagent_type": "changelog:writer", "prompt": "go", "description": "d"}
        self.send(
            "PostToolUse",
            "a9",
            "changelog:writer",
            tool="Bash",
            tool_input={"command": f"python3 {self.root}/hooks/lane/result.py writer written"},
            tool_response={},
        )
        self.end("a9", "writer")
        after = self.post("Agent", {"status": "completed", "agentId": "a9"}, **given)
        self.assertEqual(
            after.context, "changelog: writer gave `written`. Start `changelog:reviewer`."
        )


class TestResults(RunTest):
    def setUp(self):
        super().setUp()
        self.typed()

    def test_a_result_whose_route_has_a_to_tells_that_start(self):
        self.assertEqual(
            self.ran("writer", "written"),
            "changelog: writer gave `written`. Start `changelog:reviewer`.",
        )

    def test_the_routes_are_followed_through_each_result(self):
        self.ran("writer", "written")
        self.assertEqual(
            self.ran("reviewer", "more"),
            "changelog: reviewer gave `more`. Start `changelog:writer`.",
        )

    def test_a_result_whose_route_ends_the_run_tells_no_more_starts_and_ends_it(self):
        self.ran("writer", "written")
        self.assertEqual(
            self.ran("reviewer", "good"),
            "changelog: reviewer gave `good`. Start no more subagents.",
        )
        self.assertEqual(self.send("Stop"), exchange.Answer())

    def test_a_role_that_ended_with_no_result_is_to_be_started_again(self):
        _, _, agent = self.start("writer")
        self.end(agent, "writer", again=True)
        self.assertEqual(
            self.notified(agent).context,
            "changelog: writer ended with no result. Start `changelog:writer` again.",
        )

    def test_a_prompt_while_the_start_runs_is_told_to_wait(self):
        self.start("writer")
        self.assertEqual(
            self.send("UserPromptSubmit", prompt="hi").context,
            f"changelog: {WAIT}",
        )

    def test_a_result_the_role_may_give_goes_on(self):
        _, _, agent = self.start("writer")
        self.assertEqual(self.give(agent, "writer", "written"), exchange.Answer())

    def test_a_result_the_role_may_not_give_is_denied_with_its_result_sentence(self):
        _, _, agent = self.start("writer")
        self.assertEqual(
            self.give(agent, "writer", "good").deny,
            f"changelog: End by running `{RESULT} writer written`.{helpers.ENDS}\n"
            "The commands you may end by:"
            f" `python3 {self.root}/hooks/lane/result.py writer written`.",
        )

    def test_a_result_the_role_may_not_give_that_comes_back_is_not_kept(self):
        _, _, agent = self.start("writer")
        bash = {"command": f"python3 {self.root}/hooks/lane/result.py writer good"}
        self.send("PostToolUse", agent, "changelog:writer", tool="Bash", tool_input=bash)
        self.assertIsNotNone(self.end(agent, "writer").block)

    def test_a_role_about_to_end_with_no_result_goes_on_once_with_its_result_sentence(self):
        _, _, agent = self.start("writer")
        self.assertEqual(
            self.end(agent, "writer").block,
            f"changelog: End by running `{RESULT} writer written`.{helpers.ENDS}",
        )

    def test_a_role_that_gave_its_result_ends(self):
        _, _, agent = self.start("writer")
        self.give(agent, "writer", "written")
        self.assertEqual(self.end(agent, "writer"), exchange.Answer())

    def test_a_role_kept_going_once_ends_with_no_result(self):
        _, _, agent = self.start("writer")
        self.assertEqual(self.end(agent, "writer", again=True), exchange.Answer())

    def test_a_role_that_starts_a_subagent_of_the_plugin_is_denied(self):
        _, _, agent = self.start("writer")
        found = self.send(
            "PreToolUse",
            agent,
            "changelog:writer",
            tool="Agent",
            tool_input={"subagent_type": "changelog:reviewer", "prompt": "p"},
        )
        self.assertEqual(
            found.deny,
            NO_START,
        )


class TestFanOut(RunTest):
    def setUp(self):
        super().setUp()
        self.routes(fan_out=["reviewer"], precedence=["more", "good"])
        self.typed()
        self.ran("writer", "written")

    def test_a_role_that_fans_out_starts_again_while_it_runs(self):
        self.start("reviewer")
        before, after, _ = self.start("reviewer")
        self.assertEqual(
            (before, after.context if after else None),
            (
                exchange.Answer(),
                f"changelog: {WAIT_ALL}",
            ),
        )

    def test_starts_at_once_give_the_result_first_in_the_order(self):
        _, _, one = self.start("reviewer")
        _, _, two = self.start("reviewer")
        self.give(one, "reviewer", "good")
        self.give(two, "reviewer", "more")
        self.end(one, "reviewer")
        self.assertEqual(
            self.notified(one).context,
            f"changelog: {WAIT_ALL}",
        )
        self.end(two, "reviewer")
        self.assertEqual(
            self.notified(two).context,
            "changelog: The 2 runs of reviewer gave `more`. Start `changelog:writer`.",
        )

    def test_starts_at_once_whose_results_no_order_holds_tell_the_maker_to_order_them(self):
        _, _, one = self.start("reviewer")
        _, _, two = self.start("reviewer")
        self.give(one, "reviewer", "good")
        self.give(two, "reviewer", "more")
        # The routes, laid again while the starts run, no longer order the results.
        path = os.path.join(self.root, "hooks", "lanes.json")
        data = json.loads(self.read(path))
        data["routes"] = helpers.ROUTES
        helpers.write(path, json.dumps(data))
        self.end(one, "reviewer")
        self.end(two, "reviewer")
        found = self.notified(two)
        told = (
            "changelog: lane cannot check the routes of write: the runs of reviewer gave results"
            " that precedence doesn't order. Tell the user: the maker of changelog must order each"
            " result of reviewer in precedence."
        )
        self.assertEqual((found.context, found.tell), (told, told))


class TestPoint(RunTest):
    def setUp(self):
        super().setUp()
        asks = {"from": "writer", "on": "asks", "waits": True}
        self.routes(routes=[*helpers.ROUTES["routes"], asks])
        path = os.path.join(self.root, "agents", "writer.md")
        helpers.write(
            path,
            self.read(path).replace(
                f"`{RESULT} writer written`", f"`{RESULT} writer written` or `{RESULT} writer asks`"
            ),
        )
        self.typed()
        self.context = self.ran("writer", "asks")
        self.agent = "a1"

    def message(self, text):
        return self.pre("SendMessage", to=self.agent, message=text)

    def test_a_result_whose_route_waits_tells_the_point_to_put_to_the_user(self):
        self.assertEqual(
            self.context,
            "changelog: writer gave `asks`. Put its point to the user as it wrote it, in your"
            " reply, and resume `changelog:writer` with their answer by SendMessage.",
        )

    def test_a_dialog_while_the_point_waits_is_denied(self):
        self.assertEqual(
            self.pre("AskUserQuestion", questions=[]).deny,
            f"changelog: {FOLLOW}\nPut the point of `changelog:writer` to the person as it wrote"
            " it, in your reply, and end your turn: their answer comes back as their next prompt.",
        )

    def test_a_start_while_the_point_waits_is_denied_with_the_point_to_put(self):
        self.assertIn("Put the point of `changelog:writer`", self.start("reviewer")[0].deny or "")

    def test_the_end_of_a_turn_while_the_point_waits_goes_on(self):
        self.assertEqual(self.send("Stop"), exchange.Answer())

    def test_the_persons_prompt_is_kept_and_the_message_to_resume_with_is_told(self):
        self.assertEqual(
            self.send("UserPromptSubmit", prompt="Use 1.2.").context,
            "changelog: Resume `changelog:writer` by SendMessage with this message, word for"
            " word:\nThe person's answer, word for word:\nUse 1.2.",
        )

    def test_each_prompt_since_the_point_goes_into_the_message_a_blank_line_between_two(self):
        self.send("UserPromptSubmit", prompt="Use 1.2.")
        self.assertTrue(
            (self.send("UserPromptSubmit", prompt="Or 1.3?").context or "").endswith(
                "Use 1.2.\n\nOr 1.3?"
            )
        )

    def test_the_message_of_the_persons_words_alone_resumes_the_role(self):
        self.send("UserPromptSubmit", prompt="Use 1.2.")
        self.assertEqual(
            self.message("The person's answer, word for word:\nUse 1.2.\n"), exchange.Answer()
        )

    def test_a_message_in_other_words_is_denied_with_the_message_to_send(self):
        self.send("UserPromptSubmit", prompt="Use 1.2.")
        self.assertEqual(
            self.message("They said 1.2").deny,
            f"changelog: {FOLLOW}\nResume `changelog:writer` by SendMessage with this message, word"
            " for word:\nThe person's answer, word for word:\nUse 1.2.",
        )

    def test_a_message_before_the_person_answers_is_denied(self):
        self.assertEqual(
            self.message("The person's answer, word for word:\n").deny,
            f"changelog: {FOLLOW}\nPut the point of `changelog:writer` to the person as it wrote"
            " it, in your reply, and end your turn: their answer comes back as their next prompt.",
        )

    def test_the_skills_command_typed_is_no_answer(self):
        self.send("UserPromptSubmit", prompt="/changelog:write")
        self.assertEqual(self.typed().context, "changelog: Start `changelog:writer`.")

    def test_a_resumed_role_gives_its_next_result_in_place_of_the_one_before(self):
        self.send("UserPromptSubmit", prompt="Use 1.2.")
        given = {"to": self.agent, "message": "The person's answer, word for word:\nUse 1.2."}
        self.post("SendMessage", {}, **given)
        self.assertIn(
            "Wait for `changelog:writer`", self.send("UserPromptSubmit", prompt="x").context or ""
        )
        self.give(self.agent, "writer", "written")
        self.end(self.agent, "writer")
        self.assertEqual(
            self.notified(self.agent).context,
            "changelog: writer gave `written`. Start `changelog:reviewer`.",
        )

    def test_a_message_to_a_running_start_is_denied_with_the_wait(self):
        self.send("UserPromptSubmit", prompt="Use 1.2.")
        self.post(
            "SendMessage",
            {},
            to=self.agent,
            message="The person's answer, word for word:\nUse 1.2.",
        )
        self.assertIn("Wait for `changelog:writer`", self.message("more").deny or "")


class TestGivenText(RunTest):
    def setUp(self):
        super().setUp()
        self.routes(command="python3 ${CLAUDE_PLUGIN_ROOT}/s.py")
        self.typed()
        self.command = f"python3 {self.root}/s.py writer"

    def test_a_start_with_the_text_the_command_printed_goes_on(self):
        self.post("Bash", {"stdout": "Write the entries.\n"}, command=self.command)
        self.assertEqual(self.start("writer", prompt="Write the entries.")[0], exchange.Answer())

    def test_a_command_that_comes_back_with_no_stdout_cannot_be_checked(self):
        found = self.post("Bash", {}, command=self.command)
        self.assertIn("the Bash call came back with no stdout", found.context or "")

    def test_a_start_with_another_text_is_denied_with_the_command_to_run(self):
        self.post("Bash", {"stdout": "Write the entries.\n"}, command=self.command)
        self.assertEqual(
            self.start("writer", prompt="Write them.")[0].deny,
            f"changelog: {FOLLOW}\nStart `changelog:writer` with what `{self.command}` printed as"
            " its prompt, word for word: run it first where you haven't.",
        )

    def test_a_start_before_the_command_ran_is_denied(self):
        self.assertIsNotNone(self.start("writer", prompt="Write the entries.")[0].deny)


class TestEndOfTurn(RunTest):
    def setUp(self):
        super().setUp()
        self.typed()

    def test_the_end_of_a_turn_with_a_start_due_goes_on_once_with_it(self):
        self.assertEqual(self.send("Stop").block, f"changelog: {FOLLOW}\nStart `changelog:writer`.")

    def test_the_end_of_a_turn_kept_going_once_ends_the_run_and_tells_whose_step_to_fix(self):
        found = self.send("Stop", stop_active=True)
        path = os.path.join(self.root, "skills", "write", "SKILL.md")
        self.assertEqual(
            (found.block, found.tell),
            (
                None,
                (
                    "changelog: lane let the run of write end with `changelog:writer` still due:"
                    f" the maker of changelog must fix step 1 of write in {path}, which starts it."
                ),
            ),
        )
        self.assertEqual(self.send("Stop"), exchange.Answer())

    def test_a_turn_ending_with_a_role_to_start_again_tells_the_step_that_gives_its_result(self):
        _, _, agent = self.start("writer")
        self.end(agent, "writer", again=True)
        found = self.send("Stop", stop_active=True)
        path = os.path.join(self.root, "agents", "writer.md")
        self.assertEqual(
            found.tell,
            "changelog: lane let the run of write end with `changelog:writer` still due, as writer"
            f" ended with no result: the maker of changelog must fix step 4 of writer in {path},"
            " which gives its result.",
        )

    def test_the_end_of_a_turn_while_a_role_runs_goes_on(self):
        self.start("writer")
        self.assertEqual(self.send("Stop"), exchange.Answer())
