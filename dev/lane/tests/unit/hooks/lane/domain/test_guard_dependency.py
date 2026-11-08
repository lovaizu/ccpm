"""The cases of guard.py's contract for a role or a skill of a dependency that the routes name, as
plugins/lane/docs/routes.md gives them in its section on a subagent of a dependency."""

import json
import os

import helpers
from helpers import exchange, guard

FOLLOW = helpers.FOLLOW
EXAMINER = [
    {"from": "write", "to": "writer"},
    {"from": "writer", "on": "written", "to": "checker:examiner"},
    {"from": "checker:examiner", "on": "asks", "waits": True},
    {"from": "checker:examiner", "on": "done"},
]
CHECK = [
    {"from": "write", "to": "writer"},
    {"from": "writer", "on": "written", "to": "checker:check"},
    {"from": "checker:check", "on": "done"},
]


class DependencyTest(helpers.PluginTest):
    def lay(self, routes):
        helpers.changelog(self.root, with_routes=True)
        manifest = {**helpers.MANIFEST, "dependencies": ["checker"]}
        helpers.write(
            os.path.join(self.root, ".claude-plugin", "plugin.json"), json.dumps(manifest)
        )
        path = os.path.join(self.root, "hooks", "lanes.json")
        data = json.loads(self.read(path))
        data["routes"] = {**helpers.ROUTES, "routes": routes}
        helpers.write(path, json.dumps(data))
        self.checker = os.path.join(self.base, "checker")
        helpers.write(
            os.path.join(self.checker, ".claude-plugin", "plugin.json"), '{"name": "checker"}'
        )

    def send(self, name, agent=None, kind=None, **fields):
        event = exchange.Event(
            name=name, session="s1", cwd=self.project, agent_id=agent, agent_type=kind, **fields
        )
        return guard.answer("changelog", self.root, self.project, event)

    def run_writer(self):
        self.send("UserPromptExpansion", command="changelog:write")
        given = {"subagent_type": "changelog:writer", "prompt": "go"}
        self.send(
            "PostToolUse",
            tool="Agent",
            tool_input=given,
            tool_response={"status": "async_launched", "agentId": "w1"},
        )
        bash = {"command": f"python3 {self.root}/hooks/lane/result.py writer written"}
        self.send(
            "PostToolUse", "w1", "changelog:writer", tool="Bash", tool_input=bash, tool_response={}
        )
        self.send("SubagentStop", "w1", "changelog:writer")
        return self.send("UserPromptSubmit", prompt="<task-notification>")

    def result(self, name, result):
        return {"command": f"python3 {self.checker}/hooks/lane/result.py {name} {result}"}


class TestRole(DependencyTest):
    def setUp(self):
        super().setUp()
        self.lay(EXAMINER)
        self.context = self.run_writer().context
        given = {"subagent_type": "checker:examiner", "prompt": "check"}
        self.started = self.send("PreToolUse", tool="Agent", tool_input=given)
        self.send(
            "PostToolUse",
            tool="Agent",
            tool_input=given,
            tool_response={"status": "async_launched", "agentId": "e1"},
        )

    def test_a_dependencys_role_the_routes_name_is_the_start_due(self):
        self.assertEqual(
            (self.context, self.started),
            ("changelog: writer gave `written`. Start `checker:examiner`.", exchange.Answer()),
        )

    def test_a_result_by_the_dependencys_result_script_moves_the_routes_on(self):
        self.send(
            "PostToolUse",
            "e1",
            "checker:examiner",
            tool="Bash",
            tool_input=self.result("examiner", "done"),
            tool_response={},
        )
        self.send("SubagentStop", "e1", "checker:examiner")
        self.assertEqual(
            self.send("UserPromptSubmit", prompt="<task-notification>").context,
            "changelog: checker:examiner gave `done`. Start no more subagents.",
        )

    def test_a_result_no_route_from_the_role_is_on_is_not_kept(self):
        self.send(
            "PostToolUse",
            "e1",
            "checker:examiner",
            tool="Bash",
            tool_input=self.result("examiner", "good"),
            tool_response={},
        )
        self.assertIsNotNone(self.send("SubagentStop", "e1", "checker:examiner").block)

    def test_a_dependencys_role_about_to_end_with_no_result_goes_on_once_with_its_commands(self):
        self.assertEqual(
            self.send("SubagentStop", "e1", "checker:examiner").block,
            "changelog: End by running `python3 ${dependency:checker}/hooks/lane/result.py examiner"
            " asks` or `python3 ${dependency:checker}/hooks/lane/result.py examiner done`."
            f"{helpers.ENDS}\n`${{dependency:checker}}` stands for the folder that holds the plugin"
            " checker.",
        )

    def test_a_dependencys_role_kept_going_once_ends(self):
        self.assertEqual(
            self.send("SubagentStop", "e1", "checker:examiner", stop_active=True), exchange.Answer()
        )

    def test_a_dependencys_role_that_starts_a_role_of_the_plugin_is_denied(self):
        given = {"subagent_type": "changelog:writer", "prompt": "p"}
        found = self.send("PreToolUse", "e1", "checker:examiner", tool="Agent", tool_input=given)
        self.assertIn("Start no subagent of this plugin", found.deny or "")

    def test_another_call_of_a_dependencys_role_goes_on_unchecked(self):
        self.assertEqual(
            self.send(
                "PreToolUse", "e1", "checker:examiner", tool="Bash", tool_input={"command": "x"}
            ),
            exchange.Answer(),
        )

    def test_a_role_of_another_plugin_the_routes_dont_name_is_not_held(self):
        self.assertEqual(self.send("SubagentStop", "x1", "checker:other"), exchange.Answer())


class TestSkill(DependencyTest):
    def setUp(self):
        super().setUp()
        self.lay(CHECK)
        self.run_writer()

    def test_a_dependencys_skill_due_is_called(self):
        self.assertEqual(
            self.send("PreToolUse", tool="Skill", tool_input={"skill": "checker:check"}),
            exchange.Answer(),
        )

    def test_a_dependencys_skill_not_due_is_denied(self):
        self.send(
            "PostToolUse", tool="Skill", tool_input={"skill": "checker:check"}, tool_response={}
        )
        found = self.send("PreToolUse", tool="Skill", tool_input={"skill": "checker:check"})
        self.assertIsNotNone(found.deny)

    def test_the_dependencys_result_script_in_the_main_conversation_ends_the_skills_move(self):
        self.send(
            "PostToolUse", tool="Skill", tool_input={"skill": "checker:check"}, tool_response={}
        )
        found = self.send(
            "PostToolUse",
            tool="Bash",
            tool_input=self.result("check", "done"),
            tool_response={"stdout": ""},
        )
        self.assertEqual(
            found.context, "changelog: checker:check gave `done`. Start no more subagents."
        )

    def test_the_end_of_a_turn_with_the_skills_move_open_goes_on_once(self):
        self.send(
            "PostToolUse", tool="Skill", tool_input={"skill": "checker:check"}, tool_response={}
        )
        self.assertIsNotNone(self.send("Stop").block)

    def test_another_command_while_the_skills_move_runs_keeps_nothing(self):
        self.send(
            "PostToolUse", tool="Skill", tool_input={"skill": "checker:check"}, tool_response={}
        )
        found = self.send(
            "PostToolUse", tool="Bash", tool_input={"command": "ls"}, tool_response={"stdout": ""}
        )
        self.assertEqual((found, self.send("Stop").block is not None), (exchange.Answer(), True))

    def test_a_skill_the_routes_dont_name_that_comes_back_is_not_kept(self):
        self.send(
            "PostToolUse", tool="Skill", tool_input={"skill": "other:skill"}, tool_response={}
        )
        self.assertEqual(
            self.send("PreToolUse", tool="Skill", tool_input={"skill": "checker:check"}),
            exchange.Answer(),
        )

    def test_another_tool_that_comes_back_in_the_main_conversation_keeps_nothing(self):
        self.assertEqual(
            self.send("PostToolUse", tool="Read", tool_input={"file_path": "a"}, tool_response={}),
            exchange.Answer(),
        )

    def test_a_dependencys_role_is_not_held_where_the_lanes_laid_cannot_be_read(self):
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), "{")
        self.assertEqual(self.send("SubagentStop", "e1", "checker:examiner"), exchange.Answer())
