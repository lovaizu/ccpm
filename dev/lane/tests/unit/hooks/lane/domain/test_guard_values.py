"""The cases of guard.py's contract for a value given for each start, and for the step lists and
items that the plugin's adapters give, as plugins/lane/docs/lanes.md gives them."""

import json
import os
from unittest import mock

import helpers
from helpers import called, exchange, guard

STEPS = (
    "import json, sys\n"
    'work = json.load(sys.stdin)["values"].get("work") or ["x"]\n'
    'step = {"says": "Make the notes.", "lanes": [{"lane": "write_step", "takes": work}]}\n'
    'first = {"says": "Run the check.", "lanes": [{"lane": "run_step", "takes": ["make check"]}]}\n'
    'print(json.dumps({"lists": [{"list": "Q1", "steps": [first, step]}]}))\n'
)


class ValuesTest(helpers.PluginTest):
    def setUp(self):
        super().setUp()
        helpers.changelog(self.root)

    def lay(self, steps, text, **role):
        helpers.write(
            os.path.join(self.root, "hooks", "lanes.json"),
            json.dumps({"subagents": [{"name": "writer", "steps": steps, **role}]}),
        )
        helpers.write(os.path.join(self.root, "agents", "writer.md"), text)

    def started(self, prompt):
        called.record("s1", "changelog").add(
            {"kind": "start", "agent": "a1", "role": "writer", "prompt": prompt, "status": "x"}
        )

    def send(self, name, tool=None, **given):
        event = exchange.Event(
            name=name,
            session="s1",
            cwd=self.project,
            agent_id="a1",
            agent_type="changelog:writer",
            tool=tool,
            tool_input=given,
        )
        return guard.answer("changelog", self.root, self.project, event)


class TestValues(ValuesTest):
    def setUp(self):
        super().setUp()
        lane = {"lane": "write_only", "takes": ["{work}"]}
        self.lay(
            [{"step": 3, "lanes": [lane]}],
            helpers.WRITER.replace(
                "into `CHANGELOG.md`.", "into `CHANGELOG.md`. Write only `{work}`."
            ),
        )

    def test_a_lane_takes_the_value_its_start_was_given(self):
        self.started('Write the notes.\n{"work": "notes.md"}')
        found = self.send("PreToolUse", "Write", file_path=os.path.join(self.project, "other.md"))
        self.assertEqual(
            found.deny,
            "changelog: Write only `{work}`.\nThe call writes"
            f" {os.path.join(self.project, 'other.md')}.",
        )

    def test_a_write_the_value_names_goes_on(self):
        self.started('{"work": "notes.md"}')
        found = self.send("PreToolUse", "Write", file_path=os.path.join(self.project, "notes.md"))
        self.assertEqual(found, exchange.Answer())

    def test_a_value_given_as_null_lets_the_call_through(self):
        self.started('{"work": null}')
        found = self.send("PreToolUse", "Write", file_path=os.path.join(self.project, "x.md"))
        self.assertEqual(found, exchange.Answer())

    def test_a_message_sent_after_the_start_gives_values_in_place_of_its_prompt(self):
        self.started('{"work": "a.md"}')
        called.record("s1", "changelog").add(
            {"kind": "message", "agent": "a1", "text": '{"work": "b.md"}'}
        )
        found = self.send("PreToolUse", "Write", file_path=os.path.join(self.project, "b.md"))
        self.assertEqual(found, exchange.Answer())

    def test_a_start_that_doesnt_come_back_in_time_cannot_be_checked(self):
        with mock.patch.object(guard, "WAIT", 0.05):
            found = self.send("PreToolUse", "Write", file_path=os.path.join(self.project, "x.md"))
        self.assertEqual(
            found.deny,
            "changelog: lane cannot check the lanes of writer: the Agent call that started writer"
            " didn't come back within 0.05 seconds. Ask the main conversation for the fix: the main"
            " conversation must start writer again. Go on with the rest of your work meanwhile.",
        )

    def test_a_values_adapter_gives_the_values_in_place_of_lanes_own_form(self):
        helpers.write(
            os.path.join(self.root, "hooks", "adapters", "values-w.py"),
            'import json\nprint(json.dumps({"values": {"work": ["c.md"]}}))\n',
        )
        lane = {"lane": "write_only", "takes": ["{work}"]}
        self.lay(
            [{"step": 3, "lanes": [lane]}],
            helpers.WRITER.replace(
                "into `CHANGELOG.md`.", "into `CHANGELOG.md`. Write only `{work}`."
            ),
            adapter="hooks/adapters/values-w.py",
        )
        self.started("Write.")
        found = self.send("PreToolUse", "Write", file_path=os.path.join(self.project, "c.md"))
        self.assertEqual(found, exchange.Answer())

    def test_a_values_adapter_that_fails_cannot_check_the_role(self):
        helpers.write(
            os.path.join(self.root, "hooks", "adapters", "values-w.py"), "import sys\nsys.exit(3)\n"
        )
        lane = {"lane": "write_only", "takes": ["{work}"]}
        self.lay(
            [{"step": 3, "lanes": [lane]}],
            helpers.WRITER.replace(
                "into `CHANGELOG.md`.", "into `CHANGELOG.md`. Write only `{work}`."
            ),
            adapter="hooks/adapters/values-w.py",
        )
        self.started("Write.")
        found = self.send("PreToolUse", "Write", file_path=os.path.join(self.project, "c.md"))
        self.assertIn(
            "hooks/adapters/values-w.py exited with 3: . Ask the main conversation for the fix: the"
            " maker of changelog must fix hooks/adapters/values-w.py.",
            found.deny or "",
        )


class TestStepsAdapter(ValuesTest):
    def setUp(self):
        super().setUp()
        helpers.write(os.path.join(self.root, "hooks", "adapters", "steps-w.py"), STEPS)
        self.lay([], helpers.WRITER, steps_adapter="hooks/adapters/steps-w.py")
        self.started('{"work": "notes.md"}')

    def test_a_later_step_of_a_list_before_the_step_due_is_denied_with_what_it_says(self):
        found = self.send("PreToolUse", "Write", file_path=os.path.join(self.project, "notes.md"))
        self.assertEqual(
            found.deny, "changelog: Run the check. Run `make check`.\n`make check` hasn't run yet."
        )

    def test_a_command_of_a_step_an_adapter_gives_may_run(self):
        self.lay(
            [{"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]}],
            helpers.WRITER.replace(
                "`git log --oneline`.", "`git log --oneline`. Run only `git log --oneline`."
            ),
            steps_adapter="hooks/adapters/steps-w.py",
        )
        self.assertEqual(self.send("PreToolUse", "Bash", command="make check"), exchange.Answer())

    def test_the_lists_an_adapter_gives_are_given_as_the_role_starts(self):
        self.assertEqual(
            self.send("SubagentStart").context,
            "changelog: The steps of Q1, in their order:\n"
            "1. Run the check. Run `make check`.\n"
            "2. Make the notes. Make `notes.md`.",
        )

    def test_a_role_started_before_its_call_came_back_is_given_no_lists(self):
        os.remove(os.path.join(called.record("s1", "changelog").folder, "record.jsonl"))
        self.assertEqual(self.send("SubagentStart"), exchange.Answer())


class TestStepsAdapterFaults(ValuesTest):
    def adapt(self, body):
        helpers.write(os.path.join(self.root, "hooks", "adapters", "steps-w.py"), body)
        self.lay([], helpers.WRITER, steps_adapter="hooks/adapters/steps-w.py")

    def step(self, takes):
        lane = {"lane": "run_step", "takes": takes}
        lists = {"lists": [{"list": "Q1", "steps": [{"says": "Run.", "lanes": [lane]}]}]}
        return f"import json\nprint(json.dumps({lists!r}))\n".replace("'", '"')

    def test_a_steps_adapter_that_fails_cannot_check_the_role(self):
        self.adapt("import sys\nsys.exit(4)\n")
        self.started("{}")
        self.assertIn(
            "steps-w.py exited with 4", self.send("PreToolUse", "Bash", command="ls").deny or ""
        )

    def test_a_lane_an_adapter_gives_that_cannot_stand_cannot_check_the_role(self):
        self.adapt(self.step([" "]))
        self.started("{}")
        self.assertIn(
            "hooks/adapters/steps-w.py gives a lane that can't stand: run_step is given an empty"
            " thing",
            self.send("PreToolUse", "Bash", command="ls").deny or "",
        )

    def test_a_lane_an_adapter_gives_naming_a_value_not_given_cannot_check_the_role(self):
        self.adapt(self.step(["make {target}"]))
        self.started("{}")
        self.assertIn(
            "the start was given no value `target`",
            self.send("PreToolUse", "Bash", command="ls").deny or "",
        )

    def test_a_lane_an_adapter_gives_naming_a_value_given_as_null_has_no_trace(self):
        self.adapt(self.step(["{work}"]).replace("run_step", "write_step"))
        self.started('{"work": null}')
        self.assertEqual(self.send("PreToolUse", "Bash", command="ls"), exchange.Answer())


class TestItemsAdapter(ValuesTest):
    def test_every_item_reads_the_items_an_adapter_gives(self):
        helpers.write(
            os.path.join(self.root, "hooks", "adapters", "items-w.py"),
            'import json\nprint(json.dumps({"items": ["N-1"]}))\n',
        )
        lane = {
            "lane": "every_item",
            "takes": ["review.md"],
            "adapter": "hooks/adapters/items-w.py",
        }
        text = helpers.WRITER.replace(
            "you wrote.",
            "you wrote. Answer every item of `review.md`. End by running"
            f" `{helpers.RESULT} writer done`.{helpers.ENDS}",
        )
        self.lay([{"step": 4, "lanes": [lane]}], text)
        helpers.write(os.path.join(self.project, "review.md"), "- B-1\n")
        self.started("Answer.")
        found = self.send(
            "PreToolUse", "Bash", command=f"python3 {self.root}/hooks/lane/result.py writer done"
        )
        self.assertEqual(
            found.deny,
            "changelog: Answer every item of `review.md`.\nNo file written since the last change of"
            f" `{os.path.join(self.project, 'review.md')}` answers `N-1`.",
        )

    def test_an_items_adapter_that_fails_cannot_check_every_item(self):
        helpers.write(
            os.path.join(self.root, "hooks", "adapters", "items-w.py"), "import sys\nsys.exit(5)\n"
        )
        lane = {
            "lane": "every_item",
            "takes": ["review.md"],
            "adapter": "hooks/adapters/items-w.py",
        }
        text = helpers.WRITER.replace(
            "you wrote.",
            "you wrote. Answer every item of `review.md`. End by running"
            f" `{helpers.RESULT} writer done`.{helpers.ENDS}",
        )
        self.lay([{"step": 4, "lanes": [lane]}], text)
        helpers.write(os.path.join(self.project, "review.md"), "- B-1\n")
        self.started("Answer.")
        found = self.send(
            "PreToolUse", "Bash", command=f"python3 {self.root}/hooks/lane/result.py writer done"
        )
        self.assertIn(
            "lane cannot check every_item on step 4 of writer: hooks/adapters/items-w.py exited"
            " with 5",
            found.deny or "",
        )
