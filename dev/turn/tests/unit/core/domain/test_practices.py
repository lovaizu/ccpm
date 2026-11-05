"""How practices.py checks a best practice's form and makes what is read of it: faults names each
fault of its form, markdown makes the Markdown a person reads, standard leaves out its ways, and
groups shares its questions among the evaluator's runs."""

import copy
import os
import unittest
from typing import Any

import helpers
from helpers import practices

DATA = {
    "goal": "The reader gets it.",
    "parts": [{"id": "a", "what": "A.", "parts": [{"id": "b", "what": "B."}]}],
    "user_benefits": [
        {"id": "Q1", "about": "a", "what": "Does it?"},
        {"id": "Q2", "about": "b, the whole", "what": "After Q1, does all?"},
    ],
    "practices": [
        {"user_benefit": "Q1", "thinking": "Think.", "steps": ["Do."]},
        {"user_benefit": "Q2", "thinking": "Then.", "steps": []},
    ],
}


def changed(change):
    data = copy.deepcopy(DATA)
    change(data)
    return practices.faults(data)


class Faults(unittest.TestCase):
    def test_a_sound_best_practice_has_none(self):
        self.assertEqual(practices.faults(DATA), [])

    def test_questions_out_of_number_order(self):
        def swap(d):
            d["user_benefits"].reverse()
            d["practices"].reverse()

        self.assertIn("questions are Q2, Q1, not numbered in order from Q1", changed(swap))

    def test_practices_not_in_the_questions_order(self):
        def swap(d):
            d["practices"].reverse()

        expected = "practices meet Q2, Q1, not each question once in its order"
        self.assertEqual(changed(swap), [expected])

    def test_a_question_with_no_method(self):
        def drop(d):
            d["practices"].pop()

        self.assertEqual(changed(drop), ["practices meet Q1, not each question once in its order"])

    def test_about_a_part_that_is_not_there(self):
        def wrong(d):
            d["user_benefits"][0]["about"] = "c"

        self.assertEqual(changed(wrong), ["Q1 is about c, which is no part"])

    def test_a_part_named_twice(self):
        def twice(d):
            d["parts"].append({"id": "a", "what": "Again."})

        self.assertEqual(changed(twice), ["part a is named more than once"])

    def test_a_question_named_in_the_text_that_is_not_there(self):
        def name(d):
            d["practices"][1]["thinking"] = "As Q3 says."

        self.assertEqual(changed(name), ["Q3 is named, but there is no such question"])

    def test_a_part_no_question_is_about(self):
        def add(d):
            d["parts"].append({"id": "c", "what": "C."})

        self.assertEqual(changed(add), ["part c has no question about it"])

    def test_no_question_about_the_whole(self):
        def narrow(d):
            d["user_benefits"][1]["about"] = "b"

        self.assertEqual(changed(narrow), ["no question is about the whole"])

    def test_a_best_practice_of_one_question_about_the_whole(self):
        data = {
            "goal": "G.",
            "user_benefits": [{"id": "Q1", "about": "the whole", "what": "Does it?"}],
            "practices": [{"user_benefit": "Q1", "thinking": "T.", "steps": []}],
        }
        self.assertEqual(practices.faults(data), [])

    def test_two_questions_of_one_number(self):
        def same(d):
            d["user_benefits"][1]["id"] = "Q1"
            d["practices"][1]["user_benefit"] = "Q1"

        self.assertIn("questions are Q1, Q1, not numbered in order from Q1", changed(same))

    def test_a_question_numbered_otherwise_is_not_named_as_missing(self):
        def letter(d):
            d["user_benefits"][0]["id"] = "A"
            d["practices"][0]["user_benefit"] = "A"

        self.assertEqual(
            changed(letter),
            [
                "questions are A, Q2, not numbered in order from Q1",
                "Q1 is named, but there is no such question",
            ],
        )

    def test_about_a_part_named_after_the_whole_that_is_not_there(self):
        def wrong(d):
            d["user_benefits"][0]["about"] = "z"

        self.assertEqual(changed(wrong), ["Q1 is about z, which is no part"])

    def test_a_question_named_in_a_user_benefit_that_is_not_there(self):
        def name(d):
            d["user_benefits"][0]["what"] = "Before Q3, does it?"

        self.assertEqual(changed(name), ["Q3 is named, but there is no such question"])

    def test_a_value_that_is_no_text_names_no_question(self):
        def number(d):
            d["parts"][0]["level"] = 3

        self.assertEqual(changed(number), [])


TEMPLATE = """# <Product>

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: <Product>: the product's name.

<Product> is <kind>.

## Roles

### <role>

## OKRs
"""
SECTIONS = ["the opening", "Roles", "OKRs"]
BY_TEMPLATE = {
    "goal": "The reader gets it.",
    "user_benefits": [
        {"id": "Q1", "about": "the opening, Roles", "what": "Does it?"},
        {"id": "Q2", "about": "OKRs, the whole", "what": "Does all?"},
    ],
    "practices": DATA["practices"],
}


class Sections(unittest.TestCase):
    def test_the_opening_and_each_second_level_heading(self):
        self.assertEqual(practices.sections(TEMPLATE), SECTIONS)

    def test_an_opening_on_the_line_right_under_the_title(self):
        self.assertEqual(practices.sections("# <P>\n<P> is.\n## Roles\n"), ["the opening", "Roles"])

    def test_no_opening_where_only_the_title_and_notes_stand_before_the_first_section(self):
        bare = "# <P> UX\n\n> [!NOTE]\n> DELETE_TEMPLATE_COMMENT:\n> - <slot>: what.\n\n## Roles\n"
        self.assertEqual(practices.sections(bare), ["Roles"])

    def test_an_opening_right_under_a_note(self):
        text = "# <P>\n\n> [!NOTE]\n> DELETE_TEMPLATE_COMMENT: Delete.\n<P> is.\n## Roles\n"
        self.assertEqual(practices.sections(text), ["the opening", "Roles"])

    def test_a_quote_of_the_work_s_own_is_an_opening(self):
        text = "# <P>\n\n> [!NOTE]\n> <P> is not yet released.\n\n## Roles\n"
        self.assertEqual(practices.sections(text), ["the opening", "Roles"])


class NotesLeft(unittest.TestCase):
    def test_a_note_of_a_markdown_template_by_its_line(self):
        text = "# t\n\n> [!NOTE]\n> DELETE_TEMPLATE_COMMENT:\n> - <slot>: what.\n"
        self.assertEqual(practices.notes_left(text), [4])

    def test_a_note_of_a_json_template_by_its_key(self):
        text = '{\n "goal": "g",\n "x": {\n  "DELETE_TEMPLATE_COMMENT": "y"\n }\n}'
        self.assertEqual(practices.notes_left(text), [4])

    def test_lines_counted_from_a_first_line_that_is_blank(self):
        text = "\n> [!NOTE]\n> DELETE_TEMPLATE_COMMENT: what.\n"
        self.assertEqual(practices.notes_left(text), [3])

    def test_the_marker_named_in_a_sentence_is_no_note(self):
        steps = '{"steps": ["Open each note with `DELETE_TEMPLATE_COMMENT:`."]}'
        text = steps + "\nSay > DELETE_TEMPLATE_COMMENT:"
        self.assertEqual(practices.notes_left(text), [])


class Keys(unittest.TestCase):
    def test_each_key_in_order_but_the_comments(self):
        text = (
            '{"DELETE_TEMPLATE_COMMENT": "x", "goal": "<g>", "user_benefits": [], "practices": []}'
        )
        self.assertEqual(practices.keys(text), ["goal", "user_benefits", "practices"])

    def test_keeps_a_key_that_sorts_before_the_comments(self):
        self.assertEqual(
            practices.keys('{"$anchor": "a", "DELETE_TEMPLATE_COMMENT": "x"}'), ["$anchor"]
        )


class Beside(helpers.testing.FolderTest):
    """template and missing, on the files a best practice names beside it."""

    def setUp(self) -> None:
        super().setUp()
        self.folder = os.path.join(self.base, "kind")
        self.path = os.path.join(self.folder, "best-practice.json")

    def test_none_where_it_names_no_template(self):
        self.assertIsNone(practices.template(self.path, DATA))
        self.assertEqual(practices.missing(self.path, DATA), [])

    def test_the_sections_of_a_template_in_markdown(self):
        self.write(os.path.join(self.folder, "template.md"), TEMPLATE)
        named = dict(BY_TEMPLATE, template="template.md")
        self.assertEqual(practices.template(self.path, named), SECTIONS)

    def test_the_keys_of_a_template_in_json(self):
        self.write(
            os.path.join(self.folder, "template.json"),
            '{"DELETE_TEMPLATE_COMMENT": "x", "goal": "g"}',
        )
        named = dict(BY_TEMPLATE, template="template.json")
        self.assertEqual(practices.template(self.path, named), ["goal"])

    def test_each_file_named_that_is_not_there(self):
        self.write(os.path.join(self.folder, "template.md"), TEMPLATE)
        named = dict(BY_TEMPLATE, template="template.md", example="example.md")
        self.assertEqual(
            practices.missing(self.path, named), ["its example example.md is not beside it"]
        )

    def test_an_example_in_the_folder_of_another_kind(self):
        named = dict(DATA, example="../other/best-practice.json")
        self.write_json(self.path, named)
        self.write(os.path.join(self.base, "other", "best-practice.json"), "{}")
        self.assertEqual(practices.missing(self.path, named), [])

    def test_the_kind_is_the_name_of_its_folder(self):
        self.assertEqual(practices.kind_of(self.path), "kind")


class Shown(unittest.TestCase):
    def test_each_figure_under_its_folder_by_its_path_without_the_place_in_it(self):
        text = "![A](a.svg) and ![B](images/b.svg#part)\n"
        self.assertEqual(practices.shown(text), ["a.svg", "images/b.svg"])

    def test_a_figure_after_a_code_block_and_none_in_it(self):
        text = "![A](a.svg)\n```text\n![Q](q.svg)\n```\n![B](b.svg)\n```\n![R](r.svg)\n```\n"
        self.assertEqual(practices.shown(text), ["a.svg", "b.svg"])

    def test_no_link_figure_on_another_site_or_figure_above_its_folder(self):
        text = "[c](c.md) ![W](https://example.com/w.svg) ![U](../u.svg)\n"
        self.assertEqual(practices.shown(text), [])


class Leftovers(helpers.testing.FolderTest):
    """leftovers, each file in a best practice's folder that neither it, its template nor its
    example holds."""

    def setUp(self) -> None:
        super().setUp()
        self.folder = os.path.join("practices", "kind")
        self.path = os.path.join(self.folder, "best-practice.json")
        self.data = dict(DATA, template="template.md", example="example.md")
        self.write(self.at("best-practice.json"), "{}")
        self.write(self.at("best-practice.md"), "# kind\n")
        self.write(self.at("template.md"), "![The product](images/template-a.svg)\n")
        self.write(self.at("images", "template-a.svg"), "<svg/>")
        self.write(self.at("example.md"), "![P](images/a.svg)\n```text\n![Q](images/q.svg)\n```\n")
        self.write(self.at("images", "a.svg"), "<svg/>")

    def at(self, *path: str) -> str:
        return os.path.join(self.folder, *path)

    def test_none_where_each_file_is_its_own_or_a_figure_its_template_or_example_shows(self):
        self.assertEqual(practices.leftovers(self.path, self.data), [])

    def test_a_file_none_of_them_holds(self):
        self.write(self.at("images", "old.svg"), "<svg/>")
        self.write(self.at("notes.md"), "n")
        self.assertEqual(
            practices.leftovers(self.path, self.data),
            [self.at("images", "old.svg"), self.at("notes.md")],
        )

    def test_a_hidden_file_is_no_leftover(self):
        self.write(self.at("images", ".DS_Store"), "")
        self.assertEqual(practices.leftovers(self.path, self.data), [])

    def test_a_figure_the_old_copy_shows_is_a_leftover_once_its_source_dropped_it(self):
        data = dict(self.data, source="../../doc/source.md")
        self.write(os.path.join("doc", "source.md"), "No figure.\n")
        self.assertEqual(practices.leftovers(self.path, data), [self.at("images", "a.svg")])

    def test_an_example_with_no_template_keeps_the_figures_it_shows(self):
        data = dict(DATA, example="example.md")
        self.assertEqual(
            practices.leftovers(self.path, data),
            [self.at("images", "template-a.svg"), self.at("template.md")],
        )

    def test_a_source_with_no_example_keeps_only_its_own_files(self):
        data = dict(DATA, source="../../doc/source.md")
        self.assertEqual(
            practices.leftovers(self.path, data),
            [
                self.at("example.md"),
                self.at("images", "a.svg"),
                self.at("images", "template-a.svg"),
                self.at("template.md"),
            ],
        )


class Copies(helpers.testing.FolderTest):
    """copies, the files of an example that is a copy of the document its source names."""

    def setUp(self) -> None:
        super().setUp()
        self.path = os.path.join("practices", "kind", "best-practice.json")
        self.data = dict(DATA, example="example.md", source="../../doc/source.md")
        self.copy = os.path.join("practices", "kind", "example.md")

    def made(self, text: str) -> dict[str, bytes]:
        self.write(os.path.join("doc", "source.md"), text)
        return practices.copies(self.path, self.data)

    def test_none_where_it_names_no_source(self):
        self.assertEqual(practices.copies(self.path, DATA), {})

    def test_the_source_as_it_is_where_it_links_nothing(self):
        self.assertEqual(self.made("# Doc\n\nText.\n"), {self.copy: b"# Doc\n\nText.\n"})

    def test_a_link_reaches_from_the_copy_what_it_reached_from_the_source(self):
        made = self.made("[a](other.md#part) and [b](../LICENSE)\n")
        self.assertEqual(made[self.copy], b"[a](../../doc/other.md#part) and [b](../../LICENSE)\n")

    def test_a_link_to_a_page_a_place_in_it_or_another_site_is_kept(self):
        text = "[a](https://example.com/x) [b](#part) [c](mailto:a@b.c)\n"
        self.assertEqual(self.made(text)[self.copy], text.encode())

    def test_a_figure_under_the_source_is_copied_beside_the_copy(self):
        self.write(os.path.join("doc", "images", "idea.svg"), "<svg/>")
        made = self.made("![Idea](images/idea.svg)\n")
        self.assertEqual(made[self.copy], b"![Idea](images/idea.svg)\n")
        self.assertEqual(made[os.path.join("practices", "kind", "images", "idea.svg")], b"<svg/>")

    def test_a_figure_above_the_source_is_linked_where_it_is(self):
        made = self.made("![Idea](../idea.svg)\n")
        self.assertEqual(made, {self.copy: b"![Idea](../../idea.svg)\n"})

    def test_a_link_in_a_code_block_is_text_and_kept(self):
        text = "```text\n[a](other.md)\n```\n[b](other.md)\n"
        self.assertEqual(
            self.made(text)[self.copy], b"```text\n[a](other.md)\n```\n[b](../../doc/other.md)\n"
        )

    def test_a_source_or_figure_not_there_is_refused(self):
        with self.assertRaises(FileNotFoundError):
            practices.copies(self.path, self.data)
        with self.assertRaises(FileNotFoundError):
            self.made("![Idea](images/idea.svg)\n")


class FaultsByTemplate(unittest.TestCase):
    def by(self, change=lambda d: None):
        data = copy.deepcopy(BY_TEMPLATE)
        change(data)
        return practices.faults(data, SECTIONS)

    def test_questions_about_its_sections_have_none(self):
        self.assertEqual(self.by(), [])

    def test_about_what_is_no_section(self):
        def wrong(d):
            d["user_benefits"][0]["about"] = "the opening, Scenarios, Roles"

        self.assertEqual(
            self.by(wrong), ["Q1 is about Scenarios, which is no section of the template"]
        )

    def test_a_section_no_question_is_about(self):
        def narrow(d):
            d["user_benefits"][0]["about"] = "Roles"

        self.assertEqual(self.by(narrow), ["section the opening has no question about it"])

    def test_parts_beside_the_template(self):
        def add(d):
            d["parts"] = [{"id": "Roles", "what": "R."}]

        self.assertEqual(self.by(add), ["parts are kept, though the template holds the form"])


class Markdown(unittest.TestCase):
    def test_names_the_source_its_example_is_copied_from(self):
        named = dict(DATA, example="example.md", source="../../README.md")
        text = practices.markdown("kind", named)
        self.assertIn(
            "## Example\n\n[example.md](example.md),"
            " a copy of [../../README.md](../../README.md)\n",
            text,
        )

    def test_links_the_template_and_the_example_it_names(self):
        named = dict(BY_TEMPLATE, template="template.md", example="example.md")
        text = practices.markdown("kind", named)
        self.assertIn("## Template\n\n[template.md](template.md)\n", text)
        self.assertIn("## Example\n\n[example.md](example.md)\n", text)
        self.assertNotIn("## Template", practices.markdown("kind", DATA))
        self.assertNotIn("## Example", practices.markdown("kind", DATA))

    def test_holds_each_part_question_and_method_under_its_question(self):
        text = practices.markdown("kind", DATA)
        expected = ["# kind", "The reader gets it.", "## Parts", "- **a**: A.", "  - **b**: B."]
        expected += ["- **Q1** (a): Does it?", "### Q1: Does it?", "**Thinking**: Think."]
        expected.append("1. Do.")
        for line in expected:
            self.assertIn(line, text)
        self.assertLess(text.index("## User benefits"), text.index("## Practices"))

    def test_sets_each_part_under_the_one_it_is_in(self):
        c: dict[str, Any] = {"id": "c", "what": "C."}
        b: dict[str, Any] = {"id": "b", "what": "B.", "parts": [c]}
        data = {**DATA, "parts": [{"id": "a", "what": "A.", "parts": [b]}]}
        lines = practices.markdown("kind", data).splitlines()
        start = lines.index("## Parts") + 2
        self.assertEqual(
            lines[start : start + 3], ["- **a**: A.", "  - **b**: B.", "    - **c**: C."]
        )

    def test_leaves_out_what_a_best_practice_has_none_of(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        text = practices.markdown("kind", data)
        self.assertNotIn("## Parts", text)
        self.assertEqual(text.count("**Steps**"), 1)


class Standard(unittest.TestCase):
    def test_gives_the_goal_parts_and_questions_alone(self):
        # Given: a best practice with its practices
        # When: its standard is taken out
        # Then: the practices are left out, the rest as written
        self.assertEqual(
            practices.standard(DATA),
            {"goal": DATA["goal"], "parts": DATA["parts"], "user_benefits": DATA["user_benefits"]},
        )

    def test_a_best_practice_of_no_parts_gives_none(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        self.assertNotIn("parts", practices.standard(data))


class Groups(unittest.TestCase):
    def questions(self, *abouts):
        """A best practice whose questions are about the parts given, one each, in order."""
        return {"user_benefits": [{"id": f"Q{n}", "about": a} for n, a in enumerate(abouts, 1)]}

    def test_questions_about_the_same_parts_go_together(self):
        # Given: Q1 and Q3 about part a, Q2 about b
        data = self.questions("a", "b", "a")
        # Then: Q1 and Q3 go in one group, Q2 in another, each question named with the kind
        self.assertEqual(
            practices.groups(data, "k"),
            [{"id": "G1", "questions": ["k/Q1", "k/Q3"]}, {"id": "G2", "questions": ["k/Q2"]}],
        )

    def test_a_question_about_two_parts_joins_their_groups(self):
        data = self.questions("a", "b", "a, b", "c")
        self.assertEqual(
            practices.groups(data, "k"),
            [
                {"id": "G1", "questions": ["k/Q1", "k/Q2", "k/Q3"]},
                {"id": "G2", "questions": ["k/Q4"]},
            ],
        )

    def test_a_join_found_late_takes_in_a_group_made_before(self):
        # Given: Q2 about b, then Q3 joining c, which Q1 is about, to b
        data = self.questions("c", "b", "b, c")
        self.assertEqual(
            practices.groups(data, "k"), [{"id": "G1", "questions": ["k/Q1", "k/Q2", "k/Q3"]}]
        )

    def test_a_join_takes_in_the_parts_of_each_group_it_joins(self):
        # Given: Q2 about b and c, then Q3 joining a and b, then Q4 about c alone
        data = self.questions("a", "b, c", "a, b", "c")
        # Then: Q4 goes with the others, as c came in with Q2's group
        self.assertEqual(
            practices.groups(data, "k"),
            [{"id": "G1", "questions": ["k/Q1", "k/Q2", "k/Q3", "k/Q4"]}],
        )

    def test_questions_of_the_whole_go_in_one_group(self):
        data = self.questions("the whole", "a", "b, the whole")
        self.assertEqual(
            practices.groups(data, "k"),
            [{"id": "G1", "questions": ["k/Q1", "k/Q3"]}, {"id": "G2", "questions": ["k/Q2"]}],
        )


if __name__ == "__main__":
    unittest.main()
