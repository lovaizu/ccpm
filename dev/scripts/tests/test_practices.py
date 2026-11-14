"""dev/scripts/practices.py, what a person or CI runs on rn's best practices: faults names each
fault of a best practice's form, and markdown_of makes the Markdown a person reads. form names those
faults, its Markdown left behind, and each file in its folder that neither it nor its template
holds. markdown writes its Markdown beside it."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import sys
import unittest
from typing import Any

import helpers

sys.path.insert(0, os.path.join(helpers.TOP, "dev", "scripts"))

import practices


def ran(*argv):
    """What practices.py gives on the arguments: its exit code, what it printed, and its errors."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = practices.main(list(argv))
    return code, out.getvalue(), err.getvalue()


DATA: dict[str, Any] = {
    "goal": {
        "what": "The reader gets it.",
        "critical_success_factors": [
            {
                "id": "C1",
                "what": "A.",
                "necessary_conditions": [
                    {
                        "id": "N1",
                        "about": "the whole",
                        "what": "Does it?",
                        "why": "Think.",
                        "items": [
                            {
                                "at": "decide",
                                "text": "Choose.",
                                "trace": {"action": "run", "takes": ["make", "make all"]},
                            },
                            {"at": "make", "text": "Where it fails, mend it."},
                        ],
                    }
                ],
            },
            {
                "id": "C2",
                "what": "B.",
                "necessary_conditions": [
                    {
                        "id": "N2",
                        "about": "the whole",
                        "what": "After N1, does all?",
                        "why": "Then.",
                        "items": [{"at": "make", "text": "Do."}],
                    }
                ],
            },
        ],
    },
    "inputs": [],
    "preconditions": [],
}


# A best practice of the kind `kind`, beside no other kind's.
PATH = os.path.join("kind", "best-practice.json")


def factor(data: dict[str, Any], n: int) -> dict[str, Any]:
    """The factor at the place n, from 1, in the data."""
    return data["goal"]["critical_success_factors"][n - 1]


def condition(data: dict[str, Any], n: int) -> dict[str, Any]:
    """The one condition of the factor at the place n, from 1, in the data."""
    return factor(data, n)["necessary_conditions"][0]


def changed(change):
    data = copy.deepcopy(DATA)
    change(data)
    return practices.faults(data)


class Tree(unittest.TestCase):
    """The goal tree, which holds each condition under the factor it serves: the factors and the
    conditions each numbered once from 1."""

    def test_a_sound_best_practice_has_none(self):
        self.assertEqual(practices.faults(DATA), [])

    def test_factors_out_of_number_order(self):
        def swap(d):
            d["goal"]["critical_success_factors"].reverse()

        self.assertIn("factors are C2, C1, not numbered in order from C1", changed(swap))

    def test_conditions_numbered_out_of_the_order_of_their_factors_have_none(self):
        # Given: N2 under the first factor and N1 under the second, as a condition added late to an
        # earlier factor keeps the ID that roles cite it by
        def late(d):
            condition(d, 1)["id"], condition(d, 2)["id"] = "N2", "N1"
            condition(d, 2)["what"] = "Does all?"

        # Then: no fault, as each ID is there once
        self.assertEqual(changed(late), [])

    def test_two_conditions_of_one_number(self):
        def same(d):
            condition(d, 2)["id"] = "N1"

        self.assertIn("conditions are N1, N1, not N1 to N2, each once", changed(same))

    def test_a_number_left_out(self):
        def gap(d):
            condition(d, 2)["id"] = "N3"
            condition(d, 2)["what"] = "Does all?"

        self.assertEqual(changed(gap), ["conditions are N1, N3, not N1 to N2, each once"])

    def test_a_condition_numbered_otherwise_is_not_named_as_missing(self):
        def letter(d):
            condition(d, 1)["id"] = "A"

        self.assertEqual(
            changed(letter),
            [
                "conditions are A, N2, not N1 to N2, each once",
                "N1 is named, but there is no such condition",
            ],
        )


class Faults(unittest.TestCase):
    def test_about_a_section_where_it_names_no_template(self):
        def wrong(d):
            condition(d, 1)["about"] = "c"

        self.assertEqual(changed(wrong), ["N1 is about c, which is no section of the template"])

    def test_a_question_named_in_the_text_that_is_not_there(self):
        def name(d):
            condition(d, 2)["why"] = "As N3 says."

        self.assertEqual(changed(name), ["N3 is named, but there is no such condition"])

    def test_a_question_named_in_a_question_that_is_not_there(self):
        def name(d):
            condition(d, 1)["what"] = "Before N3, does it?"

        self.assertEqual(changed(name), ["N3 is named, but there is no such condition"])

    def test_a_question_named_in_a_factor_that_is_not_there(self):
        def name(d):
            factor(d, 1)["what"] = "As N3 asks."

        self.assertEqual(changed(name), ["N3 is named, but there is no such condition"])

    def test_a_value_that_is_no_text_names_no_question(self):
        def number(d):
            d["goal"]["level"] = 3

        self.assertEqual(changed(number), [])

    def test_a_step_of_a_case_that_carries_a_trace(self):
        # Given: a step that holds only where its case does, opening with Where or If, with a trace
        expected = (
            "N1.2 holds only in its case, so it carries no trace, as a run outside the case never"
            " makes it"
        )
        for opening in ("Where it fails", "If it fails"):

            def traced(d, opening=opening):
                condition(d, 1)["items"][1] = {
                    "at": "make",
                    "text": f"{opening}, mend it.",
                    "trace": {"action": "write", "takes": ["a.md"]},
                }

            # Then: the trace is a fault, as not every run makes it
            with self.subTest(opening=opening):
                self.assertEqual(changed(traced), [expected])

    def test_a_step_with_a_fault_after_one_with_no_trace(self):
        # Given: a step with no trace, then one of a case with a trace, under the second factor
        def traced(d):
            condition(d, 2)["items"] = [
                {"at": "make", "text": "Do."},
                {
                    "at": "make",
                    "text": "If it fails, mend it.",
                    "trace": {"action": "run", "takes": ["make"]},
                },
            ]

        # Then: the later step's trace is still named
        expected = (
            "N2.2 holds only in its case, so it carries no trace, as a run outside the case never"
            " makes it"
        )
        self.assertEqual(changed(traced), [expected])

    def test_a_step_that_opens_with_a_word_holding_where_or_if_is_no_case(self):
        def traced(d):
            condition(d, 1)["items"][0]["text"] = "Wherever it runs, Iffy, do it."

        self.assertEqual(changed(traced), [])

    def test_a_trace_that_takes_an_empty_text(self):
        for empty in ("", " "):

            def traced(d, empty=empty):
                condition(d, 2)["items"] = [
                    {
                        "at": "make",
                        "text": "Do.",
                        "trace": {"action": "read", "takes": ["a.md", empty]},
                    }
                ]

            with self.subTest(empty=empty):
                self.assertEqual(
                    changed(traced),
                    ["N2.1 takes an empty text in its trace, which no call matches"],
                )

    def test_a_decide_item_after_a_make_item(self):
        # Given: a practice whose item taken while deciding comes after one taken while making
        def late(d):
            condition(d, 1)["items"].append({"at": "decide", "text": "Choose again."})

        # Then: the check names the late item, as the maker settles the decisions before it makes
        expected = "N1.3 is taken while deciding, after N1.2, which is taken while making"
        self.assertEqual(changed(late), [expected])

    def test_decide_items_after_make_items_of_another_practice_are_no_fault(self):
        # Given: a practice of decide items only, after one that ends with a make item
        def other(d):
            condition(d, 2)["items"] = [{"at": "decide", "text": "Choose."}]

        self.assertEqual(changed(other), [])

    def test_an_item_named_in_the_text_that_is_not_there(self):
        # Given: a text naming the third item of N1, which has two, and the first of N2
        def name(d):
            condition(d, 2)["why"] = "As N1.3 says, and N2.1."

        # Then: the check names only the item that isn't there
        self.assertEqual(changed(name), ["N1.3 is named, but there is no such item"])

    def test_an_item_of_a_condition_that_is_not_there(self):
        def name(d):
            condition(d, 2)["why"] = "As N3.1 says."

        self.assertEqual(
            changed(name),
            [
                "N3 is named, but there is no such condition",
                "N3.1 is named, but there is no such item",
            ],
        )

    def test_an_item_numbered_zero_is_not_there(self):
        def name(d):
            condition(d, 2)["why"] = "As N1.0 says."

        self.assertEqual(changed(name), ["N1.0 is named, but there is no such item"])


TEMPLATE = """# <Product>

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: <Product>: the product's name.

<Product> is <kind>.

## Roles

### <role>

## OKRs
"""
SECTIONS = ["the opening", "Roles", "OKRs"]
BY_TEMPLATE = copy.deepcopy(DATA)
condition(BY_TEMPLATE, 1)["about"] = "the opening, Roles"
condition(BY_TEMPLATE, 2)["about"] = "OKRs, the whole"


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
    """keys, the sections of a template in JSON: each key at any depth, by its path from the top."""

    def test_each_key_at_any_depth_in_order_but_the_comments(self):
        # Given: a key in an object, and keys in each object of a list, with a comment at each level
        text = json.dumps(
            {
                "DELETE_TEMPLATE_COMMENT": "x",
                "goal": {"DELETE_TEMPLATE_COMMENT": "y", "what": "<g>"},
                "steps": [{"at": "a"}, {"at": "b", "text": "t"}],
                "inputs": [],
            }
        )
        # Then: each key once, under the keys it lies in
        self.assertEqual(
            practices.keys(text),
            [
                ("goal",),
                ("goal", "what"),
                ("steps",),
                ("steps", "at"),
                ("steps", "text"),
                ("inputs",),
            ],
        )

    def test_keeps_a_key_that_sorts_before_the_comments(self):
        self.assertEqual(
            practices.keys('{"$anchor": "a", "DELETE_TEMPLATE_COMMENT": "x"}'), [("$anchor",)]
        )

    def test_the_fields_at_any_depth_of_a_template_that_is_a_json_schema(self):
        # Given: a field inside a field, a field of each item of a list, and one through a $ref to a
        # definition that refers back to itself
        text = json.dumps(
            {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "description": "d",
                "type": "object",
                "properties": {
                    "goal": {"type": "object", "properties": {"what": {"type": "string"}}},
                    "steps": {"type": "array", "items": {"$ref": "#/$defs/step"}},
                },
                "$defs": {
                    "step": {
                        "type": "object",
                        "properties": {"text": {}, "steps": {"items": {"$ref": "#/$defs/step"}}},
                    }
                },
            }
        )
        # Then: each field by its path, the definition walked once on each path
        self.assertEqual(
            practices.keys(text),
            [("goal",), ("goal", "what"), ("steps",), ("steps", "text"), ("steps", "steps")],
        )


class Beside(helpers.FolderTest):
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
        self.assertEqual(practices.template(self.path, named), [(s,) for s in SECTIONS])

    def test_a_template_that_is_a_json_schema_it_reads_whole_has_no_fault(self):
        self.write(
            os.path.join(self.folder, "template.json"),
            '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object"}',
        )
        named = dict(BY_TEMPLATE, template="template.json")
        self.assertEqual(practices.unread(self.path, named), [])

    def test_a_template_that_is_a_json_schema_with_a_keyword_it_does_not_read(self):
        self.write(
            os.path.join(self.folder, "template.json"),
            '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "thing"}',
        )
        named = dict(BY_TEMPLATE, template="template.json")
        (fault,) = practices.unread(self.path, named)
        self.assertIn("its template template.json is no schema it reads whole", fault)

    def test_a_template_in_json_that_is_no_json(self):
        self.write(os.path.join(self.folder, "template.json"), "{")
        named = dict(BY_TEMPLATE, template="template.json")
        (fault,) = practices.unread(self.path, named)
        self.assertIn("is not JSON", fault)

    def test_a_template_in_json_that_is_no_schema_is_not_read_as_one(self):
        self.write(
            os.path.join(self.folder, "template.json"),
            '{"DELETE_TEMPLATE_COMMENT": "x", "goal": "g"}',
        )
        named = dict(BY_TEMPLATE, template="template.json")
        self.assertEqual(practices.unread(self.path, named), [])

    def test_a_template_in_markdown_is_not_read_as_a_schema(self):
        self.write(os.path.join(self.folder, "template.md"), TEMPLATE)
        named = dict(BY_TEMPLATE, template="template.md")
        self.assertEqual(practices.unread(self.path, named), [])

    def test_the_keys_of_a_template_in_json(self):
        self.write(
            os.path.join(self.folder, "template.json"),
            '{"DELETE_TEMPLATE_COMMENT": "x", "goal": "g"}',
        )
        named = dict(BY_TEMPLATE, template="template.json")
        self.assertEqual(practices.template(self.path, named), [("goal",)])

    def test_each_kind_it_takes_with_no_best_practice_beside_or_among_rn_s_own(self):
        named = dict(DATA, inputs=["note", "gone"], preconditions=["late", "note"])
        self.write(os.path.join(self.base, "note", "best-practice.json"), "{}")
        self.write(os.path.join(self.base, "late", "template.md"), "# <P>\n")
        self.assertEqual(
            practices.missing(self.path, named),
            [
                "its input gone has no best practice beside it or among rn's own",
                "its precondition late has no best practice beside it or among rn's own",
            ],
        )

    def test_a_kind_it_takes_among_rn_s_own_where_none_lies_beside(self):
        named = dict(DATA, inputs=["readme"])
        self.assertEqual(practices.missing(self.path, named), [])
        self.assertEqual(
            practices.practice_of(self.path, "readme"),
            os.path.join(practices.OWN, "readme", "best-practice.json"),
        )

    def test_a_kind_beside_it_before_rn_s_own(self):
        self.write(os.path.join(self.base, "readme", "best-practice.json"), "{}")
        self.assertEqual(
            practices.practice_of(self.path, "readme"),
            os.path.join(self.base, "readme", "best-practice.json"),
        )

    def test_a_kind_neither_beside_nor_among_rn_s_own_is_sought_beside(self):
        self.assertEqual(
            practices.practice_of(self.path, "gone"),
            os.path.join(self.base, "gone", "best-practice.json"),
        )

    def test_the_markdown_links_each_kind_it_takes_where_its_best_practice_lies(self):
        self.write(os.path.join(self.base, "late", "best-practice.json"), "{}")
        named = dict(DATA, inputs=["late", "readme", "gone"])
        own = os.path.relpath(os.path.join(practices.OWN, "readme"), self.folder)
        own = own.replace(os.sep, "/")
        self.assertIn(
            "## Inputs\n\n- [late](../late/best-practice.md)\n"
            f"- [readme]({own}/best-practice.md)\n- [gone](../gone/best-practice.md)\n",
            practices.markdown_of(self.path, named),
        )

    def test_the_entries_at_the_top_of_a_template_that_is_a_folder(self):
        for entry in (".claude-plugin/plugin.json", "skills/up/SKILL.md", "README.md", ".DS_Store"):
            self.write(os.path.join(self.folder, "template", entry), "x")
        named = dict(BY_TEMPLATE, template="template")
        self.assertEqual(
            practices.template(self.path, named), [(".claude-plugin",), ("README.md",), ("skills",)]
        )
        self.assertEqual(practices.missing(self.path, named), [])

    def test_a_template_folder_that_is_not_there(self):
        named = dict(BY_TEMPLATE, template="template")
        self.assertEqual(
            practices.missing(self.path, named), ["its template template is not beside it"]
        )

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


class Leftovers(helpers.FolderTest):
    """leftovers, each file in a best practice's folder that neither it nor its template holds."""

    def setUp(self) -> None:
        super().setUp()
        self.folder = os.path.join("practices", "kind")
        self.path = os.path.join(self.folder, "best-practice.json")
        self.data = dict(DATA, template="template.md")
        self.write(self.at("best-practice.json"), "{}")
        self.write(self.at("best-practice.md"), "# kind\n")
        self.write(
            self.at("template.md"),
            "![The product](images/template-a.svg)\n```text\n![Q](images/q.svg)\n```\n",
        )
        self.write(self.at("images", "template-a.svg"), "<svg/>")

    def at(self, *path: str) -> str:
        return os.path.join(self.folder, *path)

    def test_none_where_each_file_is_its_own_or_a_figure_its_template_shows(self):
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

    def test_each_file_of_a_template_that_is_a_folder_is_held(self):
        data = dict(DATA, template="template")
        self.write(self.at("template", "skills", "up", "SKILL.md"), "s")
        self.write(self.at("template", ".claude-plugin", "plugin.json"), "{}")
        self.assertEqual(
            practices.leftovers(self.path, data),
            [self.at("images", "template-a.svg"), self.at("template.md")],
        )

    def test_with_no_template_only_its_own_files_are_held(self):
        self.assertEqual(
            practices.leftovers(self.path, DATA),
            [self.at("images", "template-a.svg"), self.at("template.md")],
        )


class FaultsByTemplate(unittest.TestCase):
    def by(self, change=lambda d: None, sections=SECTIONS):
        data = copy.deepcopy(BY_TEMPLATE)
        change(data)
        return practices.faults(data, sections)

    def test_questions_about_its_sections_have_none(self):
        self.assertEqual(self.by(), [])

    def test_about_what_is_no_section(self):
        def wrong(d):
            condition(d, 1)["about"] = "the opening, Scenarios, Roles"

        self.assertEqual(
            self.by(wrong), ["N1 is about Scenarios, which is no section of the template"]
        )

    def test_a_section_no_question_is_about(self):
        def narrow(d):
            condition(d, 1)["about"] = "Roles"

        self.assertEqual(self.by(narrow), ["section the opening has no condition about it"])

    def test_no_question_about_the_whole_is_no_fault(self):
        def narrow(d):
            condition(d, 2)["about"] = "OKRs"

        self.assertEqual(self.by(narrow), [])

    def test_a_section_named_twice(self):
        self.assertEqual(
            self.by(sections=[*SECTIONS, "Roles"]), ["section Roles is named more than once"]
        )


# The sections of a template in JSON, each key by its path from the top.
NESTED: list[tuple[str, ...]] = [
    ("goal",),
    ("goal", "factors"),
    ("goal", "factors", "id"),
    ("inputs",),
]


class FaultsByNestedTemplate(unittest.TestCase):
    """faults, on a template in JSON, whose sections are its keys at any depth."""

    def by(self, first: str, second: str = "inputs") -> list[str]:
        data = copy.deepcopy(DATA)
        condition(data, 1)["about"], condition(data, 2)["about"] = first, second
        return practices.faults(data, NESTED)

    def test_a_condition_about_a_key_inside_another_has_none(self):
        # Given: a condition about the key factors, which lies inside goal
        # Then: no fault, as factors is a section, and goal and id are held through it
        self.assertEqual(self.by("factors"), [])

    def test_a_key_inside_a_named_key_needs_no_condition_of_its_own(self):
        self.assertEqual(self.by("goal"), [])

    def test_about_a_key_that_is_at_no_depth(self):
        self.assertEqual(
            self.by("factors, steps"), ["N1 is about steps, which is no section of the template"]
        )

    def test_a_key_that_no_condition_names_at_any_depth(self):
        self.assertEqual(
            self.by("factors", "the whole"), ["section inputs has no condition about it"]
        )


class Markdown(unittest.TestCase):
    def test_links_the_template_it_names(self):
        named = dict(BY_TEMPLATE, template="template.md")
        text = practices.markdown_of(PATH, named)
        self.assertIn("## Template\n\n[template.md](template.md)\n", text)
        self.assertNotIn("## Template", practices.markdown_of(PATH, DATA))

    def test_links_each_kind_it_takes_after_the_template(self):
        named = dict(DATA, template="template.md", inputs=["a"], preconditions=["b", "c"])
        text = practices.markdown_of(PATH, named)
        self.assertIn(
            "[template.md](template.md)\n\n## Inputs\n\n- [a](../a/best-practice.md)\n\n"
            "## Preconditions\n\n- [b](../b/best-practice.md)\n- [c](../c/best-practice.md)\n\n"
            "## Practices\n",
            text,
        )

    def test_leaves_out_a_list_of_kinds_that_is_empty(self):
        text = practices.markdown_of(PATH, dict(DATA, preconditions=["b"]))
        self.assertNotIn("## Inputs", text)
        self.assertIn("## Preconditions", text)
        self.assertNotIn("## Preconditions", practices.markdown_of(PATH, DATA))

    def test_lists_the_goal_each_factor_under_it_and_each_condition_under_its_factor(self):
        # Given: a best practice whose conditions lie under two factors, with a template's sections
        # Then: the goal tree opens the page, each condition with the sections that hold it
        self.assertTrue(
            practices.markdown_of(PATH, BY_TEMPLATE).startswith(
                "# `kind`\n\n## Goal tree\n\n"
                "- The reader gets it.\n"
                "  - **C1** A.\n"
                "    - **N1** Does it? (the opening, Roles)\n"
                "  - **C2** B.\n"
                "    - **N2** After N1, does all? (OKRs, the whole)\n\n"
            )
        )

    def test_holds_each_practice_under_its_question(self):
        text = practices.markdown_of(PATH, DATA)
        self.assertTrue(
            text.endswith(
                "## Practices\n\n"
                "### N1\n\nDoes it?\n\nThink.\n\n"
                "1. *While deciding.* Choose. The trace: `make` or `make all` run.\n"
                "2. *While making.* Where it fails, mend it.\n\n"
                "### N2\n\nAfter N1, does all?\n\nThen.\n\n"
                "1. *While making.* Do.\n"
            ),
            text,
        )

    def test_the_practices_go_in_the_order_of_their_ids_whatever_factor_holds_each(self):
        # Given: N2 under the first factor and N1 under the second
        data = copy.deepcopy(DATA)
        condition(data, 1)["id"], condition(data, 2)["id"] = "N2", "N1"
        text = practices.markdown_of(PATH, data)
        # Then: the tree keeps each under its factor, and the practices go N1, then N2
        self.assertIn("  - **C1** A.\n    - **N2** Does it? (the whole)\n", text)
        self.assertIn("## Practices\n\n### N1\n\nAfter N1, does all?\n", text)
        self.assertIn("### N2\n\nDoes it?\n", text)
        self.assertLess(text.index("### N1"), text.index("### N2"))

    def test_the_practices_go_in_number_order_past_nine(self):
        data = copy.deepcopy(DATA)
        condition(data, 1)["id"], condition(data, 2)["id"] = "N10", "N9"
        text = practices.markdown_of(PATH, data)
        self.assertLess(text.index("### N9"), text.index("### N10"))

    def test_names_each_trace_by_its_call(self):
        # Given: a step of each action, one taking three calls
        items = [
            {"at": "make", "text": "Run.", "trace": {"action": "run", "takes": ["make"]}},
            {
                "at": "make",
                "text": "Read.",
                "trace": {"action": "read", "takes": ["a.md", "b.md", "c.md"]},
            },
            {
                "at": "make",
                "text": "Make.",
                "trace": {"action": "write", "takes": ["{deliverable}"]},
            },
        ]
        data = copy.deepcopy(DATA)
        condition(data, 2)["items"] = items
        # Then: each names its calls, the last after or, and what the call does
        self.assertIn(
            "1. *While making.* Run. The trace: `make` run.\n"
            "2. *While making.* Read. The trace: `a.md`, `b.md` or `c.md` read to its end.\n"
            "3. *While making.* Make. The trace: `{deliverable}` made.\n",
            practices.markdown_of(PATH, data),
        )


class Practices(helpers.FolderTest):
    """form and markdown, on a best practice of the kind `kind`."""

    def setUp(self) -> None:
        super().setUp()
        self.folder = os.path.join(self.base, "kind")
        self.path = os.path.join(self.folder, "best-practice.json")
        self.write_json(self.path, DATA)

    def test_form_fails_until_markdown_writes_it(self):
        self.assertEqual(ran("form", self.path)[0], 1)
        self.assertEqual(ran("markdown", self.path), (0, "", ""))
        self.assertEqual(
            self.read(os.path.join(self.folder, "best-practice.md")),
            practices.markdown_of(self.path, DATA),
        )
        self.assertEqual(ran("form", self.path), (0, "", ""))

    def test_form_fails_on_a_fault_of_the_form(self):
        data = copy.deepcopy(DATA)
        condition(data, 2)["id"] = "N1"
        self.write_json(self.path, data)
        ran("markdown", self.path)
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"practices.py: {self.path}: {practices.faults(data)[0]}", err)

    def test_form_refuses_a_tree_out_of_its_nesting(self):
        # Given: each way a best practice could leave the tree that the goal holds
        def flat_goal(d):
            d["goal"] = "The reader gets it."

        def no_factor(d):
            d["goal"]["critical_success_factors"] = []

        def empty_factor(d):
            factor(d, 2)["necessary_conditions"] = []

        def no_items(d):
            del condition(d, 1)["items"]

        def named_factor(d):
            condition(d, 1)["csf"] = "C1"

        def beside(key):
            return lambda d: d.update({key: []})

        conditions = "$.goal.critical_success_factors"
        cases = [
            (flat_goal, '$.goal: expected an object, found "The reader gets it."'),
            (no_factor, f"{conditions}: expected 1 or more items, found 0"),
            (empty_factor, f"{conditions}[1].necessary_conditions: expected 1 or more items"),
            (no_items, f'{conditions}[0].necessary_conditions[0]: expected the key "items"'),
            (named_factor, f"{conditions}[0].necessary_conditions[0]: expected only the keys"),
            (beside("practices"), "$: expected only the keys"),
            (beside("parts"), "$: expected only the keys"),
            (beside("necessary_conditions"), "$: expected only the keys"),
        ]
        for change, where in cases:
            with self.subTest(where=where):
                data = copy.deepcopy(DATA)
                change(data)
                self.write_json(self.path, data)
                code, _, err = ran("form", self.path)
                # Then: the form refuses it, at the place it left the tree
                self.assertEqual(code, 1)
                self.assertIn(f"is out of its form: {where}", err)

    def test_form_holds_the_questions_to_the_template_beside_it(self):
        data = copy.deepcopy(DATA)
        data["template"] = "template.md"
        self.write_json(self.path, data)
        self.write(os.path.join(self.folder, "template.md"), "# <P>\n\n## Use\n")
        ran("markdown", self.path)
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"practices.py: {self.path}: section Use has no condition about it", err)
        self.assertIn(
            "[template.md](template.md)", self.read(os.path.join(self.folder, "best-practice.md"))
        )

    def test_form_holds_the_questions_to_a_template_that_is_a_folder_and_keeps_its_files(self):
        data = copy.deepcopy(DATA)
        data["template"] = "template"
        self.write_json(self.path, data)
        self.write(os.path.join(self.folder, "template", "skills", "up", "SKILL.md"), "# up\n")
        ran("markdown", self.path)
        self.assertEqual(
            ran("form", self.path),
            (1, "", f"practices.py: {self.path}: section skills has no condition about it\n"),
        )

    def test_form_fails_on_a_template_it_names_that_is_not_beside_it(self):
        self.write_json(self.path, dict(DATA, template="template.md"))
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"practices.py: {self.path}: its template template.md is not beside it", err)

    def test_form_fails_on_a_json_out_of_its_schema(self):
        self.write_json(self.path, {"goal": "g"})
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn("is out of its form", err)

    def test_form_fails_on_a_best_practice_that_names_no_kinds_it_takes(self):
        for key in ("inputs", "preconditions"):
            with self.subTest(key=key):
                data = copy.deepcopy(DATA)
                del data[key]
                self.write_json(self.path, data)
                code, _, err = ran("form", self.path)
                self.assertEqual(code, 1)
                self.assertIn(f'is out of its form: $: expected the key "{key}"', err)

    def test_form_fails_on_a_kind_it_takes_that_has_no_best_practice(self):
        self.write_json(self.path, dict(DATA, inputs=["gone"]))
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(
            f"practices.py: {self.path}: its input gone has no best practice beside it"
            " or among rn's own",
            err,
        )

    def test_form_fails_on_a_markdown_changed_by_hand(self):
        made = practices.markdown_of(self.path, DATA)
        for changed in (made + "More.\n", made[:-1]):
            with self.subTest(changed=changed[-6:]):
                self.write(os.path.join(self.folder, "best-practice.md"), changed)
                code, _, err = ran("form", self.path)
                self.assertEqual(code, 1)
                self.assertIn(
                    "best-practice.md is not as its JSON makes it; run practices.py markdown", err
                )

    def test_form_says_to_remove_a_leftover(self):
        ran("markdown", self.path)
        stray = os.path.join(self.folder, "notes.md")
        self.write(stray, "n")
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(
            f"practices.py: {self.path}: {stray} is neither the best practice's nor its"
            " template's; remove it",
            err,
        )

    def test_each_command_names_a_json_it_cannot_read(self):
        self.write(self.path, "{")
        for command in ("form", "markdown"):
            with self.subTest(command=command):
                code, _, err = ran(command, self.path)
                self.assertEqual(code, 1)
                self.assertIn(f"practices.py: {self.path}: {self.path} is not JSON", err)
        self.assertFalse(os.path.exists(os.path.join(self.folder, "best-practice.md")))

    def test_form_names_a_best_practice_that_is_not_there(self):
        # Given: a path where no file lies.
        gone = os.path.join(self.folder, "gone.json")
        # When: form runs on it.
        code, _, err = ran("form", gone)
        # Then: it fails, and names the path.
        self.assertEqual(code, 1)
        self.assertIn(f"practices.py: {gone}: there is no file {gone}", err)

    def test_a_command_it_does_not_take_gives_2_with_its_usage(self):
        # When: practices.py gets a command that is neither form nor markdown.
        code, _, err = ran("check", self.path)
        # Then: it gives 2, and says what it takes.
        self.assertEqual((code, err), (2, practices.USAGE + "\n"))

    def test_a_command_with_no_best_practice_gives_2_with_its_usage(self):
        # When: practices.py gets a command and no best practice to run it on.
        code, _, err = ran("form")
        # Then: it gives 2, and says what it takes.
        self.assertEqual((code, err), (2, practices.USAGE + "\n"))


if __name__ == "__main__":
    unittest.main()
