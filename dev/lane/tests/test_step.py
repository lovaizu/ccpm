"""A subagent's step, read from its file in the plugin's agents/: the file found by the name Claude
Code gives the subagent, and the step's text, a line break read as a space."""

import os
import unittest

import helpers
from helpers import step


class TestAgentFile(helpers.PluginTest):
    def test_the_file_is_found_by_the_name_in_its_frontmatter(self):
        # Given: the subagent changelog-writer kept in agents/writer.md
        # When: its file is looked for by its name
        # Then: it is that file
        self.assertEqual(step.agent_file(self.plugin, "changelog-writer"), self.agent_file)

    def test_a_name_quoted_in_the_frontmatter_is_found(self):
        # Given: a subagent whose name is quoted in its frontmatter
        self.write(os.path.join(self.plugin, "agents", "q.md"), '---\nname: "quoted"\n---\n')
        # When: its file is looked for by its name
        # Then: it is found
        self.assertEqual(
            step.agent_file(self.plugin, "quoted"), os.path.join(self.plugin, "agents", "q.md")
        )

    def test_a_name_is_read_as_claude_code_reads_its_frontmatter(self):
        # Given: a subagent whose name has a comment after it, after a key of several lines and
        # another key
        text = "---\ndescription: >\n  Writes.\ntools: Read\nname: commented # the writer\n---\n"
        self.write(os.path.join(self.plugin, "agents", "c.md"), text)
        # When: its file is looked for by its name
        # Then: it is found, the comment no part of the name
        self.assertEqual(
            step.agent_file(self.plugin, "commented"), os.path.join(self.plugin, "agents", "c.md")
        )

    def test_no_file_is_found_for_a_name_no_subagent_has(self):
        # Given: files of other subagents, one of no frontmatter, one whose frontmatter does not
        # close, and a file that is no Markdown
        self.write(os.path.join(self.plugin, "agents", "plain.md"), "name: other\n")
        self.write(os.path.join(self.plugin, "agents", "open.md"), "---\nname: other\n")
        self.write(os.path.join(self.plugin, "agents", "other.txt"), "---\nname: other\n---\n")
        for name in ("other", "a", "z"):
            with self.subTest(name=name):
                # When: a file is looked for by a name none has
                # Then: none is found
                self.assertIsNone(step.agent_file(self.plugin, name))

    def test_no_file_is_found_in_a_plugin_without_agents(self):
        # Given: a plugin with no agents/ folder
        # When: a subagent's file is looked for
        # Then: none is found
        self.assertIsNone(step.agent_file(self.base, "changelog-writer"))

    def test_a_name_in_the_body_is_not_taken_for_the_subagents(self):
        # Given: a file whose frontmatter names another subagent, the name looked for in its body
        self.write(os.path.join(self.plugin, "agents", "b.md"), "---\nname: b\n---\nname: x\n")
        # When: a file is looked for by the name in the body
        # Then: none is found
        self.assertIsNone(step.agent_file(self.plugin, "x"))


class TestSpan(unittest.TestCase):
    def lines(self, text: str = helpers.STEPS) -> list[str]:
        """The lines of the subagent's file of the text."""
        return text.splitlines()

    def test_a_step_is_its_numbered_line_in_the_steps(self):
        # Given: the subagent's steps
        lines = self.lines()
        # When: step 1 is looked for
        # Then: it is its numbered line alone
        self.assertEqual(step.span(lines, 1), (12, 13))

    def test_a_step_ends_before_its_list_of_in_and_out(self):
        # Given: step 3 with an Out line under it
        # When: it is looked for
        # Then: it is its numbered line, the Out line left out
        self.assertEqual(step.span(self.lines(), 3), (14, 15))

    def test_a_step_takes_the_lines_its_text_goes_on_in(self):
        # Given: a step right under the heading whose text goes on over two more lines, then a
        # blank line
        text = "## Steps\n1. One\n   two\n   three\n\n   four\n"
        # When: it is looked for
        # Then: it is its numbered line and the two lines that go on from it
        self.assertEqual(step.span(self.lines(text), 1), (1, 4))

    def test_a_step_ends_where_the_next_begins(self):
        # Given: a step whose text goes on over one more line, its next step indented by no space
        text = "## Steps\n1. One\n   two\n2. Two\n"
        # When: the first is looked for
        # Then: it is its numbered line and the line that goes on from it
        self.assertEqual(step.span(self.lines(text), 1), (1, 3))

    def test_a_step_on_the_line_right_after_the_heading_is_found(self):
        # Given: Steps after a line of their own, the first step right under the heading
        text = "Intro\n## Steps\n1. One\n"
        # When: it is looked for
        # Then: it is found on the line after the heading
        self.assertEqual(step.span(self.lines(text), 1), (2, 3))

    def test_a_numbered_line_outside_the_steps_is_no_step(self):
        # Given: a numbered list in the Role before the Steps, and a heading after them
        text = "## Role\n\n2. Not a step\n\n## Steps\n\n1. One\n\n## Notes\n\n2. Not a step\n"
        # When: step 2 is looked for
        # Then: none is found
        self.assertIsNone(step.span(self.lines(text), 2))

    def test_a_line_opening_with_a_mark_in_a_code_fence_does_not_end_the_steps(self):
        # Given: Steps holding a code fence with a comment line opening with `#`, a step after it
        text = "## Steps\n\n1. One\n\n```sh\n# a comment\n```\n\n2. Two\n"
        # When: the step after the fence is looked for
        # Then: it is found on its line
        self.assertEqual(step.span(self.lines(text), 2), (8, 9))

    def test_a_steps_heading_in_a_code_fence_is_not_the_steps(self):
        # Given: a code fence showing a Steps heading and a step, before the Steps themselves
        text = "```\n## Steps\n1. Shown\n```\n\n## Steps\n\n1. One\n"
        # When: step 1 is looked for
        # Then: it is the one in the Steps, not the one in the fence
        self.assertEqual(step.span(self.lines(text), 1), (7, 8))

    def test_a_step_no_line_numbers_is_not_found(self):
        # Given: the subagent's four steps
        # When: step 5 is looked for, and step 13, whose number begins no line though 1 and 3 do
        # Then: neither is found
        self.assertIsNone(step.span(self.lines(), 5))
        self.assertIsNone(step.span(self.lines(), 13))


class TestSays(helpers.PluginTest):
    def test_a_steps_text_reads_a_line_break_as_a_space(self):
        # Given: a step whose text goes on over a second line, indented
        lines = ["## Steps", "", "3. Write it. Do not run `git commit`", "   or `git push`."]
        # When: its text is read
        # Then: the line break and the indent after it read as one space
        self.assertEqual(
            step.says(lines, (2, 4)), "3. Write it. Do not run `git commit` or `git push`."
        )

    def test_a_sentence_the_step_says_over_a_line_break_holds(self):
        # Given: step 3 saying the sentence over a line break
        text = helpers.STEPS.replace(
            "`CHANGELOG.md`.\n", "`CHANGELOG.md`. Do not run `git commit`\n   or `git push`.\n"
        )
        self.write(self.agent_file, text)
        # When: whether it holds the sentence is asked
        # Then: it does
        self.assertTrue(step.holds(self.plugin, "changelog-writer", 3, helpers.SENTENCE))

    def test_a_sentence_the_step_no_longer_says_does_not_hold(self):
        # Given: step 3 as it was before the lane was laid
        # When: whether it holds the sentence is asked
        # Then: it does not
        self.assertFalse(step.holds(self.plugin, "changelog-writer", 3, helpers.SENTENCE))

    def test_a_step_or_subagent_no_longer_there_does_not_hold(self):
        # Given: a step number the file no longer has, and a subagent no file names
        # When: whether either holds the sentence is asked
        # Then: neither does
        self.assertFalse(step.holds(self.plugin, "changelog-writer", 9, helpers.SENTENCE))
        self.assertFalse(step.holds(self.plugin, "gone", 3, helpers.SENTENCE))


class TestExpanded(unittest.TestCase):
    def test_the_plugins_folder_is_put_in_where_the_text_names_it(self):
        # Given: a sentence naming a file of the plugin by ${CLAUDE_PLUGIN_ROOT}, twice
        said = "Read `${CLAUDE_PLUGIN_ROOT}/a.md` and `${CLAUDE_PLUGIN_ROOT}/b.md`."
        # When: it is given as Claude Code gives the subagent its step
        # Then: the plugin's folder stands in each place, as the subagent reads it
        self.assertEqual(step.expanded(said, "/p"), "Read `/p/a.md` and `/p/b.md`.")


if __name__ == "__main__":
    unittest.main()
