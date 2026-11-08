"""A subagent's step, read from its file in the plugin's agents/: the file found by the name in its
frontmatter, as Claude Code takes it, and the step's text, its numbered line under `## Steps` and
the lines its text goes on in, each line break read as a space."""

import os
import unittest

import helpers
from helpers import step


class TestAgentFile(helpers.PluginTest):
    def test_the_file_is_found_by_the_name_in_its_frontmatter(self):
        # Given: writer kept in agents/writer.md, and another file beside it
        self.write(os.path.join(self.plugin, "agents", "a.md"), "---\nname: reviewer\n---\n")
        # When: its file is looked for by its name
        # Then: it is that file
        self.assertEqual(step.agent_file(self.plugin, "writer"), self.agent_file)

    def test_no_file_is_found_for_a_name_no_file_gives(self):
        for agents in (True, False):
            with self.subTest(agents=agents):
                # Given: agents/ holding writer and a file that is no Markdown, or no agents/
                self.write(os.path.join(self.plugin, "agents", "notes.txt"), "name: lead\n")
                if not agents:
                    os.rename(os.path.join(self.plugin, "agents"), os.path.join(self.base, "x"))
                # When: a file is looked for by another name
                # Then: none is found
                self.assertIsNone(step.agent_file(self.plugin, "lead"))


class TestSpan(unittest.TestCase):
    def test_a_step_runs_from_its_numbered_line_through_the_lines_it_goes_on_in(self):
        lines = ["## Steps", "", "1. One", "2. Two,", "   still two.", "   - In: a", "3. Three"]
        # Given: a step that goes on in an indented line, then has a list under it
        # When: where it is is found
        # Then: it is its line and the one it goes on in, the list left out
        self.assertEqual(step.span(lines, 2), (3, 5))
        self.assertEqual(step.says(lines, (3, 5)), "2. Two, still two.")

    def test_a_step_going_on_in_one_line_ends_after_it(self):
        lines = ["## Steps", "", "1. One,", "   still one.", "2. Two"]
        # Given: step 1 on the third line, going on in the fourth
        # When: where it is is found
        # Then: it runs through the fourth
        self.assertEqual(step.span(lines, 1), (2, 4))

    def test_a_step_is_looked_for_under_steps_alone(self):
        for before in ("## Role", "## Usage", "### Note"):
            lines = [before, "2. Not a step.", "## Steps", "1. One", "## After", "2. Not one."]
            for number, where in ((1, (3, 4)), (2, None)):
                with self.subTest(before=before, number=number):
                    # Given: numbered lines under a heading before the Steps, of their level or
                    # another, and after them
                    # When: a step is looked for
                    # Then: it is found under the Steps alone
                    self.assertEqual(step.span(lines, number), where)

    def test_a_file_without_steps_has_none(self):
        # Given: a file with no `## Steps`
        # When: a step is looked for
        # Then: none is found
        self.assertIsNone(step.span(["1. One"], 1))


class TestLast(unittest.TestCase):
    def test_the_last_step_is_the_highest_number_under_steps(self):
        for lines, last in (
            (["## Steps", "1. One", "2. Two", "   - Out: x", "## After", "3. Not one."], 2),
            (["## Steps", "", "Text."], None),
            (["1. One"], None),
        ):
            with self.subTest(lines=lines):
                # Given: Steps of two steps with a heading after, Steps of none, or no Steps
                # When: the last step is looked for
                # Then: it is step 2, or none
                self.assertEqual(step.last(lines), last)


class TestHolds(helpers.PluginTest):
    def test_a_step_saying_the_sentence_holds_it(self):
        # Given: writer with the README's lanes laid
        self.lay()
        # When: step 2 is asked whether it says run_only's sentence
        # Then: it does
        self.assertTrue(step.holds(self.plugin, "writer", 2, helpers.RUN))

    def test_a_step_not_saying_the_sentence_does_not_hold_it(self):
        for name, number in (("writer", 2), ("writer", 9), ("lead", 2)):
            with self.subTest(name=name, number=number):
                # Given: writer with no lane laid
                # When: a step of it, one it does not have, or one of a subagent no file
                # gives, is asked whether it says run_only's sentence
                # Then: it does not
                self.assertFalse(step.holds(self.plugin, name, number, helpers.RUN))


class TestPart(helpers.PluginTest):
    def entry(self, body: str) -> None:
        """writer's entry with the body."""
        self.write(self.agent_file, f"---\nname: writer\n---\n\n{body}\n")

    def test_the_one_file_under_domain_the_body_names_twice_is_the_part(self):
        # Given: writer's body naming its part twice
        self.entry(
            "Read `${CLAUDE_PLUGIN_ROOT}/domain/w.md`, and"
            " `${CLAUDE_PLUGIN_ROOT}/domain/w.md` again."
        )
        # When: its part is looked for
        # Then: it is that file, whether it is there or not, and its steps are read from it
        part = os.path.join(self.plugin, "domain", "w.md")
        self.assertEqual(
            (step.part(self.plugin, "writer"), step.steps_file(self.plugin, "writer")), (part, part)
        )
        self.assertEqual(step.lines_of(self.plugin, "writer"), [])
        self.write(part, "## Steps\n\n1. Go.\n")
        self.assertEqual(step.lines_of(self.plugin, "writer"), ["## Steps", "", "1. Go."])

    def test_the_one_markdown_file_under_domain_the_body_names_is_the_part(self):
        # Given: writer's body naming its part under domain/, as an entry of a plugin with parts
        # does, and the JSON Schema of its values beside it
        self.entry(
            "Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/writer.md`, and your values are in the"
            " form of `${CLAUDE_PLUGIN_ROOT}/domain/writer-in.schema.json`."
        )
        # When: its part is looked for
        # Then: it is the Markdown file, a schema being no part
        part = os.path.join(self.plugin, "domain", "writer.md")
        self.assertEqual(step.part(self.plugin, "writer"), part)

    def test_a_part_is_named_by_the_role_not_by_the_subagent(self):
        # Given: writer's body naming its role's flow under domain/, beside a form elsewhere
        self.entry(
            "`claim.json` below is `${CLAUDE_PLUGIN_ROOT}/forms/claim.json`.\n"
            "Read `${CLAUDE_PLUGIN_ROOT}/domain/writing.md` whole first."
        )
        # When: its part is looked for
        # Then: it is that file, by the name of the role, not of the subagent
        part = os.path.join(self.plugin, "domain", "writing.md")
        self.assertEqual(step.part(self.plugin, "writer"), part)
        self.assertEqual(step.steps_file(self.plugin, "writer"), part)

    def test_a_body_naming_no_part_or_more_than_one_has_its_steps_in_the_entry(self):
        for body in (
            "Work on.",
            "Read `${CLAUDE_PLUGIN_ROOT}/domain/a.md` and `${CLAUDE_PLUGIN_ROOT}/domain/b.md`.",
            "Read `${CLAUDE_PLUGIN_ROOT}/domain/../x.md`.",
            "Read `${CLAUDE_PLUGIN_ROOT}/domain/w.json`.",
            "Read `${CLAUDE_PLUGIN_ROOT}/scripts/a.md`.",
            "Read `${CLAUDE_PLUGIN_ROOT}/prompts/a.md`.",
            "Read `${CLAUDE_PLUGIN_ROOT}/core/roles/a.md`.",
            "Read `${CLAUDE_PLUGIN_ROOT}/core/domain/a.md`.",
        ):
            with self.subTest(body=body):
                # Given: writer's body naming no part, two, one out of domain/, a file that is
                # no Markdown, or one in another folder, such as prompts/ or core/roles/, where
                # plugins laid before kept theirs
                self.entry(body)
                # When: its part is looked for
                # Then: there is none, and its steps are in its entry
                self.assertIsNone(step.part(self.plugin, "writer"))
                self.assertEqual(step.steps_file(self.plugin, "writer"), self.agent_file)
        # And: a subagent no entry names has neither
        self.assertIsNone(step.part(self.plugin, "lead"))
        self.assertIsNone(step.steps_file(self.plugin, "lead"))


class TestNumbered(helpers.PluginTest):
    def test_the_list_holds_each_step_laid_in_its_order_with_its_traces(self):
        # Given: writer's steps, with lanes laid on step 3 and step 2, a trace on each, and one on
        # step 0, which no step says
        laid = [
            helpers.rules.Laid(3, "write_step", ["CHANGELOG.md"]),
            helpers.rules.Laid(2, "run_only", ["git log --oneline"]),
            helpers.rules.Laid(2, "run_step", ["git log --oneline"]),
            helpers.rules.Laid(0, "result", ["give"]),
        ]
        self.write(self.agent_file, helpers.WRITER)
        # When: its step list is read, run_step and write_step being of the trace kind
        found = step.numbered(self.plugin, "writer", laid, {"run_step", "write_step"})
        # Then: it holds steps 2 and 3, in order, each saying its text with no number, with its
        # traces alone
        self.assertEqual(
            found,
            [
                step.Step("Read the commits since then with `git log --oneline`.", [laid[2]]),
                step.Step("Write the new entries into `CHANGELOG.md`.", [laid[0]]),
            ],
        )

    def test_a_step_the_file_no_longer_has_is_left_out(self):
        # Given: a lane laid on step 9, which writer's steps don't have
        self.write(self.agent_file, helpers.WRITER)
        laid = [helpers.rules.Laid(9, "run_step", ["make"])]
        # When: its step list is read
        # Then: it is empty
        self.assertEqual(step.numbered(self.plugin, "writer", laid, {"run_step"}), [])


class TestDue(unittest.TestCase):
    def test_the_step_due_is_the_first_with_a_trace_not_come_back(self):
        # Given: a step with no trace, one whose trace came back, and two whose traces did not
        steps = [
            step.Step("a", []),
            step.Step("b", ["done"]),
            step.Step("c", ["left"]),
            step.Step("d", ["left"]),
        ]
        # When: the step due is read, what each trace leaves missing given
        found = step.due(steps, lambda s: "" if s.traces == ["done"] else f"{s.says} missing")
        # Then: it is c, the third, with what it misses
        self.assertEqual(found, (2, "c missing"))

    def test_no_step_is_due_where_every_trace_came_back(self):
        # Given: steps whose traces each came back, or have none
        steps = [step.Step("a", []), step.Step("b", ["done"])]
        # When: the step due is read
        # Then: none is
        self.assertIsNone(step.due(steps, lambda s: ""))


class TestSkill(helpers.PluginTest):
    """A skill of the plugin, `skills/<name>/SKILL.md`, whose step the routes are laid on."""

    def test_a_skills_steps_are_in_its_skill_md_or_the_part_it_names(self):
        # Given: the README's skill write
        self.write(self.skill_file, helpers.SKILL)
        # When: its file and its steps are looked for
        # Then: they are in its SKILL.md, which says its step 1
        self.assertEqual(step.skill_file(self.plugin, "write"), self.skill_file)
        self.assertEqual(step.steps_file(self.plugin, "write", skill=True), self.skill_file)
        said = "1. Have the entries written and reviewed."
        self.assertTrue(step.holds(self.plugin, "write", 1, said, skill=True))
        # And: where its body names its part under domain/, they are in that part
        part = os.path.join(self.plugin, "domain", "orchestrator.md")
        self.write(
            self.skill_file,
            "---\nname: write\n---\n\nRead"
            " `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md` whole first.\n",
        )
        self.write(part, "## Steps\n\n1. Go.\n")
        self.assertEqual(step.steps_file(self.plugin, "write", skill=True), part)
        self.assertEqual(
            step.lines_of(self.plugin, "write", skill=True), ["## Steps", "", "1. Go."]
        )

    def test_a_skill_not_there_has_no_file(self):
        # Given: no skills/write/SKILL.md, and an agent named write
        self.write(os.path.join(self.plugin, "agents", "w.md"), "---\nname: write\n---\n")
        # When: the skill write is looked for
        # Then: it has no file, and no steps
        self.assertIsNone(step.skill_file(self.plugin, "write"))
        self.assertIsNone(step.steps_file(self.plugin, "write", skill=True))
        self.assertEqual(step.lines_of(self.plugin, "write", skill=True), [])


if __name__ == "__main__":
    unittest.main()
