"""The cases of guard.py's contract for a role's steps held in their order by their traces, a
command held for the person, and the lanes checked as the role gives its result, as the
architecture's sequences "S3: a role's call held to its steps" and "S3: a result given" draw
them."""

import json
import os

import helpers
from helpers import exchange, guard

RESULT = helpers.RESULT
STEPS = [
    {"step": 1, "lanes": [{"lane": "read_whole", "takes": ["CHANGELOG.md"]}]},
    {
        "step": 2,
        "lanes": [
            {"lane": "hold", "takes": ["git push"]},
            {"lane": "run_only", "takes": ["git log --oneline"]},
        ],
    },
    {
        "step": 3,
        "lanes": [
            {"lane": "write_step", "takes": ["CHANGELOG.md"]},
            {"lane": "read_only", "takes": ["CHANGELOG.md"]},
        ],
    },
    {"step": 4, "lanes": [{"lane": "end_when", "takes": ["CHANGELOG.md"]}]},
]
FIRST = "Read `CHANGELOG.md` to learn its last version. Read `CHANGELOG.md` to its end."
TEXT = f"""---
name: writer
background: true
---

1. {FIRST}
2. Read the commits. Run `git push` only with the person's approval. Run only `git log --oneline`.
3. Write the entries. Make `CHANGELOG.md`. Read only `CHANGELOG.md`.
4. Reply. End only once `CHANGELOG.md` is made. End by running `{RESULT} writer done`.{helpers.ENDS}
"""


class StepsTest(helpers.PluginTest):
    def setUp(self):
        super().setUp()
        helpers.changelog(self.root)
        helpers.write(os.path.join(self.root, "agents", "writer.md"), TEXT)
        lanes = {"subagents": [{"name": "writer", "steps": STEPS}]}
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), json.dumps(lanes))
        helpers.write(os.path.join(self.project, "CHANGELOG.md"), "# Changelog\n")
        self.changelog = os.path.join(self.project, "CHANGELOG.md")

    def send(self, name, tool, **given):
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

    def call(self, tool, **given):
        """The role's call, PreToolUse, then PostToolUse where it goes on: the first answer."""
        before = self.send("PreToolUse", tool, **given)
        if not before.deny:
            self.send("PostToolUse", tool, **given)
        return before

    def give(self):
        return self.call("Bash", command=f"python3 {self.root}/hooks/lane/result.py writer done")


class TestOrder(StepsTest):
    def test_a_later_steps_trace_before_the_step_due_is_denied_with_what_the_step_says(self):
        self.assertEqual(
            self.call("Write", file_path=self.changelog, content="x").deny,
            f"changelog: {FIRST}\n`{self.changelog}` is unread.",
        )

    def test_a_later_steps_trace_once_the_step_due_is_done_goes_on(self):
        self.call("Read", file_path=self.changelog)
        self.assertEqual(
            self.call("Write", file_path=self.changelog, content="x"), exchange.Answer()
        )

    def test_a_call_that_is_no_trace_goes_on_before_the_step_due(self):
        self.assertEqual(self.call("Bash", command="git log --oneline"), exchange.Answer())


class TestLanes(StepsTest):
    def test_a_command_held_for_the_person_goes_to_them_with_its_sentence(self):
        self.assertEqual(
            self.call("Bash", command="git push").ask,
            "changelog: Run `git push` only with the person's approval.",
        )

    def test_a_read_outside_the_inputs_is_denied_with_its_sentence(self):
        found = self.call("Read", file_path=os.path.join(self.project, "README.md"))
        self.assertEqual(
            found.deny,
            "changelog: Read only `CHANGELOG.md`.\n"
            f"The call reads {os.path.join(self.project, 'README.md')}.",
        )

    def test_a_read_of_the_roles_own_part_goes_on(self):
        part = os.path.join(self.root, "agents", "writer.md")
        self.assertEqual(self.call("Read", file_path=part), exchange.Answer())


class TestKept(StepsTest):
    def test_a_read_of_a_file_not_there_is_kept_with_no_lines(self):
        gone = os.path.join(self.project, "gone.md")
        self.send("PostToolUse", "Read", file_path=gone)
        kept = [e for e in guard.called.record("s1", "changelog").entries() if e["kind"] == "call"]
        self.assertEqual(kept[-1]["input"], {"file_path": gone, "lines": None})

    def test_a_form_not_there_stops_the_write_it_would_hold(self):
        steps = [
            {
                "step": 3,
                "lanes": [
                    {
                        "lane": "in_form",
                        "takes": ["CHANGELOG.md", "${CLAUDE_PLUGIN_ROOT}/gone.json"],
                    }
                ],
            }
        ]
        helpers.write(
            os.path.join(self.root, "hooks", "lanes.json"),
            json.dumps({"subagents": [{"name": "writer", "steps": steps}]}),
        )
        text = TEXT.replace(
            "Make `CHANGELOG.md`. Read only `CHANGELOG.md`.",
            "Write `CHANGELOG.md` in the form of `${CLAUDE_PLUGIN_ROOT}/gone.json`.",
        )
        helpers.write(os.path.join(self.root, "agents", "writer.md"), text)
        found = self.call("Write", file_path=self.changelog, content="{}")
        self.assertEqual(
            found.deny,
            "changelog: lane cannot check in_form on step 3 of writer: the form"
            f" {self.root}/gone.json isn't there. Ask the main conversation for the fix: the maker"
            " of changelog must lay its lanes again with Lane's lay.py write. Go on with the rest"
            " of your work meanwhile.",
        )


class TestResult(StepsTest):
    def test_a_result_before_each_trace_came_back_is_denied_with_the_first_step_left(self):
        self.assertEqual(self.give().deny, f"changelog: {FIRST}\n`{self.changelog}` is unread.")

    def test_a_result_with_a_lane_of_the_end_not_kept_is_denied_with_what_is_missing(self):
        self.call("Read", file_path=self.changelog)
        self.call("Write", file_path=self.changelog, content="x")
        os.remove(self.changelog)
        self.assertEqual(
            self.give().deny,
            f"changelog: End only once `CHANGELOG.md` is made.\n`{self.changelog}` isn't there.",
        )

    def test_a_result_with_each_step_done_and_each_lane_kept_goes_on(self):
        self.call("Read", file_path=self.changelog)
        self.call("Write", file_path=self.changelog, content="x")
        self.assertEqual(self.give(), exchange.Answer())
