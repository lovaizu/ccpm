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

    def test_a_step_is_looked_for_under_steps_alone(self):
        lines = ["## Role", "2. Not a step.", "## Steps", "1. One", "## After", "2. Not one."]
        for number, where in ((1, (3, 4)), (2, None)):
            with self.subTest(number=number):
                # Given: numbered lines before the Steps and after them
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


if __name__ == "__main__":
    unittest.main()
