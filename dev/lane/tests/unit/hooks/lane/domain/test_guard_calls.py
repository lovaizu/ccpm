"""The cases of guard.py's contract for a role's tool call held to its lanes, as the architecture's
sequence "S3: a role's call held to its steps" draws them."""

import json
import os

import helpers
from helpers import exchange, guard, testing

SESSION = "s1"


class GuardTest(testing.FolderTest):
    def setUp(self):
        super().setUp()
        self.root = os.path.join(self.base, "changelog")
        self.project = os.path.join(self.base, "project")
        os.makedirs(self.project)
        helpers.changelog(self.root)

    def call(self, tool, agent="changelog:writer", **given):
        event = exchange.Event(
            name="PreToolUse",
            session=SESSION,
            cwd=self.project,
            agent_id="a1",
            agent_type=agent,
            tool=tool,
            tool_input=given,
        )
        return guard.answer("changelog", self.root, self.project, event)

    def bash(self, text, **more):
        return self.call("Bash", command=text, **more)


class TestHeld(GuardTest):
    def test_a_command_its_lanes_name_goes_on(self):
        self.assertEqual(self.bash("git log --oneline"), exchange.Answer())

    def test_a_command_its_lanes_dont_name_is_denied_with_its_steps_sentence(self):
        self.assertEqual(
            self.bash("git commit -m x").deny,
            "changelog: Run only `git log --oneline`.\n"
            "The commands you may run: `git log --oneline`.",
        )

    def test_a_write_outside_its_outputs_is_denied_with_its_steps_sentence(self):
        found = self.call("Write", file_path="README.md", content="x")
        self.assertEqual(
            found.deny,
            "changelog: Write only `CHANGELOG.md`.\n"
            f"The call writes {os.path.join(self.project, 'README.md')}.",
        )

    def test_a_path_reads_from_the_project_folder_wherever_the_role_works(self):
        found = self.call("Write", file_path=os.path.join(self.project, "CHANGELOG.md"))
        self.assertEqual(found, exchange.Answer())

    def test_a_call_of_a_role_with_no_lanes_goes_on(self):
        self.assertEqual(self.bash("git commit", agent="changelog:reviewer"), exchange.Answer())

    def test_a_call_of_another_plugins_role_goes_on(self):
        self.assertEqual(self.bash("git commit", agent="other:writer"), exchange.Answer())

    def lay(self, steps, text=None):
        """Lays writer's lanes as given, its entry holding the text given or its laid steps."""
        path = os.path.join(self.root, "hooks", "lanes.json")
        helpers.write(path, json.dumps({"subagents": [{"name": "writer", "steps": steps}]}))
        if text is not None:
            helpers.write(os.path.join(self.root, "agents", "writer.md"), text)

    def test_a_lane_checked_only_at_the_end_lets_each_call_through(self):
        lane = {"lane": "end_when", "takes": ["CHANGELOG.md"]}
        text = helpers.WRITER.replace(
            "wrote.\n",
            "wrote. End only once `CHANGELOG.md` is made. End by running"
            f" `{helpers.RESULT} writer done`.{helpers.ENDS}\n",
        )
        self.lay([{"step": 4, "lanes": [lane]}], text)
        self.assertEqual(self.bash("git commit"), exchange.Answer())

    def test_a_part_with_no_numbered_list_has_its_lanes_held_all_the_same(self):
        text = "---\nname: writer\nbackground: true\n---\nWrite the entries.\n"
        helpers.write(os.path.join(self.root, "agents", "writer.md"), text)
        self.assertIn("Run only", self.bash("git commit").deny or "")


class TestStart(GuardTest):
    def start(self):
        event = exchange.Event(
            name="SubagentStart",
            session=SESSION,
            cwd=self.project,
            agent_id="a1",
            agent_type="changelog:writer",
        )
        return guard.answer("changelog", self.root, self.project, event)

    def test_a_role_whose_steps_say_every_sentence_is_given_nothing(self):
        self.assertEqual(self.start(), exchange.Answer())

    def test_a_part_of_its_own_is_given_whole_with_the_plugins_folder_put_in(self):
        helpers.write(
            os.path.join(self.root, "domain", "writer.md"), "Read `${CLAUDE_PLUGIN_ROOT}/a.md`.\n"
        )
        helpers.write(
            os.path.join(self.root, "agents", "writer.md"),
            "---\nname: writer\nbackground: true\n---\n"
            "Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/writer.md`.\n",
        )
        self.assertEqual(
            self.start().context,
            f"Read `{self.root}/a.md`.\n\n"
            "changelog: Run only `git log --oneline`.\n\n"
            "changelog: Write only `CHANGELOG.md`.",
        )


class TestCannotCheck(GuardTest):
    def fault(self, what, who):
        return (
            f"changelog: lane cannot check the lanes of writer: {what}. Ask the main"
            f" conversation for the fix: {who}. Go on with the rest of your work meanwhile."
        )

    def test_lanes_laid_that_cannot_be_read_stop_the_call_and_tell_the_user(self):
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), "{")
        found = self.bash("git log --oneline")
        path = os.path.join(self.root, "hooks", "lanes.json")
        self.assertEqual(
            (found.deny, found.tell),
            (
                self.fault(
                    f"{path} is no JSON: Expecting property name enclosed in double quotes:"
                    " line 1 column 2 (char 1)",
                    "the maker of changelog must lay its lanes again with Lane's lay.py write",
                ),
            )
            * 2,
        )

    def end(self, again):
        event = exchange.Event(
            name="SubagentStop",
            session=SESSION,
            cwd=self.project,
            agent_id="a1",
            agent_type="changelog:writer",
            stop_active=again,
        )
        return guard.answer("changelog", self.root, self.project, event)

    def test_lanes_laid_that_cannot_be_read_keep_the_role_going_once_as_it_ends(self):
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), "{")
        found = self.end(False)
        self.assertEqual((found.block is not None, found.block == found.tell), (True, True))

    def test_lanes_laid_that_cannot_be_read_let_a_role_kept_going_once_end(self):
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), "{")
        found = self.end(True)
        self.assertEqual((found.block, found.tell is not None), (None, True))

    def test_a_role_no_longer_set_to_run_in_the_background_stops_the_call(self):
        path = os.path.join(self.root, "agents", "writer.md")
        helpers.write(path, helpers.WRITER_LAID.replace("background: true\n", ""))
        self.assertEqual(
            self.bash("git log --oneline").deny,
            self.fault(
                f"{path} no longer sets `background: true`",
                f"the maker of changelog must set `background: true` in {path}",
            ),
        )

    def test_a_role_whose_entry_is_gone_stops_the_call(self):
        os.remove(os.path.join(self.root, "agents", "writer.md"))
        self.assertEqual(
            self.bash("git log --oneline").deny,
            self.fault(
                f"no agents/*.md names `writer` in {self.root}",
                "the maker of changelog must lay its lanes again with Lane's lay.py write",
            ),
        )

    def test_a_step_no_longer_saying_its_lanes_sentence_stops_the_call(self):
        path = os.path.join(self.root, "agents", "writer.md")
        helpers.write(path, helpers.WRITER_LAID.replace(" Run only `git log --oneline`.", ""))
        self.assertEqual(
            self.bash("git log --oneline").deny,
            "changelog: lane cannot check run_only on step 2 of writer: step 2 no longer says"
            ' "Run only `git log --oneline`.". Ask the main conversation for the fix: the'
            " maker of changelog must lay its lanes again with Lane's lay.py write. Go on with"
            " the rest of your work meanwhile.",
        )

    def test_a_step_no_longer_in_the_list_stops_the_call(self):
        path = os.path.join(self.root, "agents", "writer.md")
        helpers.write(path, helpers.WRITER_LAID.split("3. ")[0])
        self.assertIn(
            "lane cannot check write_only on step 3 of writer: the steps hold no step 3.",
            self.bash("git log --oneline").deny or "",
        )

    def test_a_lane_naming_a_value_the_start_wasnt_given_stops_the_call(self):
        lane = {"lane": "write_only", "takes": ["{work}"]}
        text = helpers.WRITER.replace("`CHANGELOG.md`.\n", "`CHANGELOG.md`. Write only `{work}`.\n")
        path = os.path.join(self.root, "hooks", "lanes.json")
        helpers.write(
            path,
            json.dumps(
                {"subagents": [{"name": "writer", "steps": [{"step": 3, "lanes": [lane]}]}]}
            ),
        )
        helpers.write(os.path.join(self.root, "agents", "writer.md"), text)
        self.assertEqual(
            self.bash("ls").deny,
            "changelog: lane cannot check write_only on step 3 of writer: the start was given no"
            " value `work`. Ask the main conversation for the fix: the maker of changelog must lay"
            " its lanes again with Lane's lay.py write. Go on with the rest of your work"
            " meanwhile.",
        )

    def test_no_project_folder_stops_the_call(self):
        event = exchange.Event(
            name="PreToolUse",
            session=SESSION,
            cwd=self.project,
            agent_id="a1",
            agent_type="changelog:writer",
            tool="Bash",
            tool_input={"command": "ls"},
        )
        found = guard.answer("changelog", self.root, None, event)
        self.assertEqual(
            found.deny,
            self.fault(
                "Claude Code gave the hook no CLAUDE_PROJECT_DIR",
                "whoever runs changelog must run it in a Claude Code that gives each hook"
                " CLAUDE_PROJECT_DIR",
            ),
        )

    def test_a_call_not_as_claude_code_documents_it_stops(self):
        self.assertEqual(
            self.call("Bash", description="no command").deny,
            self.fault(
                "the Bash call gives no command",
                "Anthropic must fix Claude Code, whose hook input isn't as its documentation"
                " gives it",
            ),
        )
