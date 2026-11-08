"""The cases of step.py's contract: a role's part, and the numbered steps in it."""

import os

from helpers import plugin, step, testing

PART = "Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/writer.md`. Carry it out.\n"


class TestPart(testing.FolderTest):
    def entry(self, body):
        self.write("agents/writer.md", "---\nname: writer\n---\n" + body)
        return plugin.subagent(self.base, "writer")

    def test_the_part_is_the_file_under_domain_that_the_entry_names(self):
        self.write("domain/writer.md", "1. Write.\n")
        found = step.part(self.base, self.entry(PART))
        self.assertEqual(found.path, os.path.join(self.base, "domain", "writer.md"))

    def test_a_part_of_its_own_file_holds_that_file_whole(self):
        self.write("domain/writer.md", "# writer\n\n1. Write.\n")
        self.assertEqual(step.part(self.base, self.entry(PART)).text, "# writer\n\n1. Write.\n")

    def test_a_part_named_twice_is_that_one_part(self):
        self.write("domain/writer.md", "1. Write.\n")
        found = step.part(self.base, self.entry(PART + PART))
        self.assertEqual(found.path, os.path.join(self.base, "domain", "writer.md"))

    def test_an_entry_naming_no_part_is_its_own_part(self):
        entry = self.entry("1. Write.\n")
        found = step.part(self.base, entry)
        self.assertEqual((found.path, found.own), (entry.path, False))

    def test_an_entry_naming_two_parts_is_its_own_part(self):
        body = "See `${CLAUDE_PLUGIN_ROOT}/domain/a.md` and `${CLAUDE_PLUGIN_ROOT}/domain/b.md`.\n"
        entry = self.entry(body)
        self.assertEqual(step.part(self.base, entry).path, entry.path)

    def test_a_file_outside_domain_names_no_part(self):
        entry = self.entry("See `${CLAUDE_PLUGIN_ROOT}/forms/notes.md`.\n")
        self.assertEqual(step.part(self.base, entry).path, entry.path)

    def test_a_part_named_but_missing_is_refused(self):
        with self.assertRaisesRegex(
            plugin.Fault, r"names its part domain/writer\.md, which isn't there"
        ):
            step.part(self.base, self.entry(PART))

    def test_the_steps_of_a_part_are_its_numbered_list(self):
        self.write("domain/writer.md", "1. Read.\n2. Write.\n")
        found = step.part(self.base, self.entry(PART))
        self.assertEqual([s.says for s in found.steps], ["Read.", "Write."])


class TestNumbered(testing.FolderTest):
    def test_each_item_keeps_its_own_number(self):
        found = step.numbered("2. Read.\n5. Write.\n")
        self.assertEqual([s.number for s in found], [2, 5])

    def test_an_item_runs_on_over_its_indented_lines(self):
        found = step.numbered("1. Read\n   the file.\n2. Write.\n")
        self.assertEqual(found[0].says, "Read\n   the file.")

    def test_an_item_runs_on_over_a_blank_line_before_an_indented_one(self):
        found = step.numbered("1. Read.\n\n   Then more.\n2. Write.\n")
        self.assertEqual(found[0].says, "Read.\n\n   Then more.")

    def test_each_item_knows_its_first_and_last_line(self):
        found = step.numbered("# Steps\n\n1. Read\n   it.\n2. Write.\n")
        self.assertEqual([(s.first, s.last) for s in found], [(2, 3), (4, 4)])

    def test_items_apart_by_a_blank_line_are_one_list(self):
        found = step.numbered("1. Read.\n\n2. Write.\n")
        self.assertEqual([s.says for s in found], ["Read.", "Write."])

    def test_the_list_ends_at_a_line_that_is_no_item_and_not_indented(self):
        found = step.numbered("1. Read.\nAfter.\n2. Not a step.\n")
        self.assertEqual([s.says for s in found], ["Read."])

    def test_only_the_first_numbered_list_holds_the_steps(self):
        found = step.numbered("1. Read.\n\n## Then\n\n1. Other.\n")
        self.assertEqual([s.says for s in found], ["Read."])

    def test_a_list_in_a_code_fence_holds_no_steps(self):
        found = step.numbered("```\n1. Code.\n```\n1. Read.\n")
        self.assertEqual([s.says for s in found], ["Read."])

    def test_a_text_with_no_numbered_list_has_no_steps(self):
        self.assertEqual(step.numbered("Do the work.\n- a point\n"), [])
